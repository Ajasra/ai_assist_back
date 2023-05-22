import os
from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate

from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain

from cocroach_utils.db_errors import save_error
from cocroach_utils.db_conv import add_conversation, get_conv_by_id
from cocroach_utils.db_history import add_history
from langchain.chains.router import MultiRetrievalQAChain

load_dotenv()

llm = ChatOpenAI(temperature=.0, model_name="gpt-3.5-turbo")

persist_directory = './db'

conversations = []
memories = []


def format_response(response_input):
    """
    Format the response
    :param response_input:
    :return:
    """
    print("Response input: ", response_input)
    data = response_input.split("FOLLOW UP QUESTIONS:")
    if len(data) > 1:
        answer = data[0].strip()
        follow_up_questions = data[1].replace("FOLLOWUP QUESTIONS:","").strip().split("\n")
        return {
            "answer": answer,
            "follow_up_questions": follow_up_questions
        }

    else:
        return {
            "answer": response_input,
            "follow_up_questions": [],
            "source": ""
        }


def get_conv_id(conv_id, user_id, doc_id):
    """
    Get the conversation id and return a new one if it does not exist
    :param conv_id:
    :param user_id:
    :param doc_id:
    :return:
    """
    cur_conv = None
    if conv_id is None or conv_id == -1 or conv_id == 0:
        cur_conv = add_conversation(user_id, doc_id, title="New conversation")
        print("New conversation added"
              "Conversation id: ", cur_conv)
    else:
        conv = get_conv_by_id(conv_id)
        if conv is None:
            save_error("Conversation not found")
            cur_conv = -1
        else:
            cur_conv = conv_id

    return cur_conv


def get_simple_response(prompt, conv_id, user_id, memory):
    """
    Get a simple response from the model
    :param user_id:
    :param prompt:
    :param conv_id:
    :param memory:
    :return:
    """

    cur_conv = get_conv_id(conv_id, user_id, 0)
    if cur_conv == -1:
        return {
            "status": "error",
            "message": "Conversation not found or can't be created",
            "conversation_id": conv_id
        }

    # system = PromptTemplate(
    #     template="You are a helpful assistant that translates {input_language} to {output_language}.",
    #     input_variables=["input_language", "output_language"],
    # )
    system = PromptTemplate(
        template="",
        input_variables=[],
    )
    system_message_prompt = SystemMessagePromptTemplate(prompt=system)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=llm, prompt=chat_prompt)

    try:
        response = chain.run(text=prompt)
        add_history(cur_conv, prompt, response)
    except Exception as e:
        save_error(e)
        return {
            "status": "error",
            "message": str(e),
            "conversation_id": cur_conv
        }

    return {
        "status": "success",
        "message": response,
        "conversation_id": cur_conv
    }


def get_response_over_doc(prompt, conv_id, doc_id, user_id, memory):
    if doc_id is not None:

        index_dir = os.path.join(persist_directory, str(doc_id))
        embeddings = OpenAIEmbeddings()
        docsearch = Chroma(persist_directory=index_dir, embedding_function=embeddings)

        cur_conv = get_conv_id(conv_id, user_id, doc_id)
        if cur_conv == -1:
            return {
                "status": "error",
                "message": "Conversation not found or can't be created",
                "conversation_id": conv_id
            }

        _DEFAULT_TEMPLATE = """Given the context information answer the following question
                            If you don't know the answer, just say you dont know Don't try to make up an answer.
                            =========
                            Always answer in the format:
                            ANSWER: <your answer>
                            FOLLOW UP QUESTIONS: <list of 3 suggested questions related to context and conversation for better understanding>
                            =========
                            question: {}""".format(prompt)

        cur_conversation = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
            return_source_documents=True
        )

        try:
            result = cur_conversation({"question": _DEFAULT_TEMPLATE})
            response = format_response(result["answer"])
            add_history(cur_conv, prompt, response["answer"])

        except Exception as e:
            save_error(e)
            return {
                "status": "error",
                "message": "Error while getting response",
                "conversation_id": cur_conv,
                "data": {
                    "response": str(e),
                }
            }

        return {
            "status": "success",
            "message": "Agent response",
            "data": {
                "response": response["answer"],
                "follow_up_questions": response["follow_up_questions"],
                "source": result["source_documents"],
                "conversation_id": cur_conv
            }
        }

    else:
        save_error("No document selected")
        return {
            "status": "error",
            "message": "No document selected",
            "conversation_id": None
        }


# TESTING AND EXPERIMENTS
def multichain():
    """
    Test multichain query
    :return:
    """
    print("Multichain")

    embeddings = OpenAIEmbeddings()
    docsearch1 = Chroma(persist_directory="./db/866136357063950337", embedding_function=embeddings).as_retriever()
    docsearch2 = Chroma(persist_directory="./db/866149744008953857", embedding_function=embeddings).as_retriever()

    retriever_infos = [
        {
            "name": "Cancer Culture",
            "description": "Good for answering questions about the Cancer culture book",
            "retriever": docsearch1
        },
        {
            "name": "History and condition for creativity",
            "description": "Good for answer questions about Creativity",
            "retriever": docsearch2
        }
    ]

    chain = MultiRetrievalQAChain.from_retrievers(llm, retriever_infos, verbose=True)

    prompt = "What is the book cancer culture about?"

    _DEFAULT_TEMPLATE = """Given the context information answer the following question
                                If you don't know the answer, just say you dont know Don't try to make up an answer.
                                =========
                                Always answer in the format:
                                ANSWER: <your answer>
                                FOLLOW UP QUESTIONS: <list of 3 suggested questions related to context and conversation for better understanding>
                                SOURCE: <do not make up source, give the page or the chapter from the document>
                                =========
                                question: {}""".format(prompt)

    response = chain.run(prompt)
    print(response)


def get_summary_response(prompt):
    """
    Get response over the multiple index test
    :param prompt:
    :return:
    """
    print("\n")
    print(prompt)
    index_dir = os.path.join(persist_directory, "summary")
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma(persist_directory=index_dir, embedding_function=embeddings)
    cur_conversation = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, chain_type="stuff",
                                                                  retriever=docsearch.as_retriever())

    _DEFAULT_TEMPLATE = """Given the context information answer the following question
                                If you don't know the answer, just say you dont know Don't try to make up an answer.
                                =========
                                Always answer in the format:
                                ANSWER: <your answer>
                                FOLLOW UP QUESTIONS: <list of 3 suggested questions related to context and conversation for better understanding>
                                SOURCE: <do not make up source, give the page or the chapter from the document>
                                =========
                                question: {}""".format(prompt)

    result = cur_conversation({"question": _DEFAULT_TEMPLATE})
    response = format_response(result["answer"])
    print(response)
    return response
