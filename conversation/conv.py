import os

import openai
import tiktoken
from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate, ConversationChain

from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.vectorstores import Chroma, DocArrayInMemorySearch
from langchain.chains import RetrievalQAWithSourcesChain, RetrievalQA

from langchain.memory import ConversationBufferMemory

from cocroach_utils.db_errors import save_error
from cocroach_utils.db_conv import add_conversation, get_conv_by_id
from cocroach_utils.db_history import add_history, get_history_for_conv
from langchain.chains.router import MultiRetrievalQAChain

from vectordb.vectordb import get_embedding_model

from cocroach_utils.db_docs import get_doc_by_id

load_dotenv()

llm = ChatOpenAI(temperature=.0, model_name="gpt-3.5-turbo", verbose=True, model_kwargs={"stream": False})

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
    data = []
    # check if there are follow up questions regardless of uppercase or lowercase
    if "FOLLOW UP QUESTIONS:" in response_input:
        data = response_input.split("FOLLOW UP QUESTIONS:")
    elif "FOLLOWUP QUESTIONS:" in response_input:
        data = response_input.split("FOLLOWUP QUESTIONS:")
    elif "Follow up questions:" in response_input:
        data = response_input.split("Follow up questions:")
    elif "Followup questions:" in response_input:
        data = response_input.split("Followup questions:")
    elif "follow up questions:" in response_input:
        data = response_input.split("follow up questions:")
    elif "followup questions:" in response_input:
        data = response_input.split("followup questions:")
    elif "Followup" in response_input:
        data = response_input.split("Followup:")
    elif "FOLLOWUP" in response_input:
        data = response_input.split("FOLLOWUP:")
    elif "followup" in response_input:
        data = response_input.split("followup:")
    elif "follow-up" in response_input:
        data = response_input.split("follow-up:")

    if len(data) > 1:
        answer = data[0].strip().replace("ANSWER:", "")
        answer = data[0].strip().replace("answer:", "")
        answer = data[0].strip().replace("Answer:", "")
        follow_up_questions = data[1].strip().split("\n")
        if len(follow_up_questions) == 1:
            follow_up_questions = data[1].strip().split("?")
        return {
            "answer": answer,
            "follow_up_questions": follow_up_questions
        }
    else:
        return {
            "answer": response_input.replace("ANSWER:", "").strip(),
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
        # cur_conv = add_conversation(user_id, doc_id, title="New conversation")
        # print("New conversation added"
        #       "Conversation id: ", cur_conv)
        pass
    else:
        conv = get_conv_by_id(conv_id)
        if conv is None:
            save_error("Conversation not found")
            cur_conv = -1
        else:
            cur_conv = conv_id

    return cur_conv


def num_tokens_from_messages(message, model="gpt-3.5-turbo"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(message, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(message, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = len(encoding.encode(message))
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


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

        user_prompt = prompt

        index_dir = os.path.join(persist_directory, str(doc_id))
        embeddings = get_embedding_model()
        docsearch = Chroma(persist_directory=index_dir, embedding_function=embeddings)

        cur_conv = get_conv_id(conv_id, user_id, doc_id)
        if cur_conv == -1:
            return {
                "status": "error",
                "message": "Conversation not found or can't be created",
                "conversation_id": conv_id
            }

        _DEFAULT_TEMPLATE = """Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question:
                            If you don't know the answer, just say you dont know Don't try to make up an answer.
                            =========
                            Always answer in the json format with the following fields:
                            "answer": "<your answer>",
                            "followup": "<list of 3 suggested questions related to context and conversation for better understanding>"
                            =========
                            ------
                            <ctx>
                            {context}
                            </ctx>
                            ------
                            <hs>
                            {history}
                            </hs>
                            ------
                            {question}
                            Answer:"""

        promptTmp = PromptTemplate(
            input_variables=["history", "context", "question"],
            template=_DEFAULT_TEMPLATE,
        )

        # _DEFAULT_TEMPLATE = prompt

        # retriever = docsearch.as_retriever(enable_limit=True, search_kwargs={"k": 6})
        retriever = docsearch.as_retriever()

        memory_obj = ConversationBufferMemory(
            memory_key="history",
            input_key="question")

        if memory != -1:
            # get history from db
            history = get_history_for_conv(cur_conv, 2)
            if history is not None:
                # from last to first
                history.reverse()
                for hist in history:
                    memory_obj.save_context(
                        {"question": hist["prompt"]},
                        {"output": hist["answer"]}
                    )


        # sources = retriever.get_relevant_documents(prompt)
        #
        # if len(sources) == 0:
        #     # TODO: Rewrite the prompt with the API (give summary of the document and the name of the document)
        #     doc = get_doc_by_id(doc_id)
        #     title = doc["name"]
        #     summary = doc["summary"]
        #
        #     # join all history
        #     hist = ""
        #     for h in history:
        #         hist += "question: " + h["prompt"] + "\n"
        #         hist += "answer: " + h["answer"] + "\n"
        #
        #     tmp = "Give a revised and optimized prompt based on the original prompt, document summary, document " \
        #                "name and history of the conversation." \
        #                "The prompt should be related to the document." \
        #                "Answer only the optimized prompt. Don't try to make up an answer." \
        #                "<document summary>"+summary+"</document summary>" \
        #                "<document name>"+title+"</document name>" \
        #                 "<history>" + hist + "</history>," \
        #                 "<original prompt>"+user_prompt+"</original prompt>"
        #
        #     system = PromptTemplate(
        #         template="",
        #         input_variables=[],
        #     )
        #     system_message_prompt = SystemMessagePromptTemplate(prompt=system)
        #     human_template = "{text}"
        #     human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        #
        #     chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        #     chain = LLMChain(llm=llm, prompt=chat_prompt)
        #
        #     try:
        #         response = chain.run(text=tmp)
        #         response = response.replace("Optimized prompt: ", "")
        #
        #         return {
        #             "status": "success",
        #             "message": "Agent response",
        #             "data": {
        #                 "response": "Sorry, I cant answer your question. Please clarify.",
        #                 "follow_up_questions": [response],
        #                 "source": [],
        #                 "conversation_id": str(cur_conv)
        #             }
        #         }
        #
        #     except Exception as e:
        #         save_error(e)
        #         return {
        #             "status": "error",
        #             "message": str(e),
        #             "conversation_id": cur_conv
        #         }

        cur_conversation = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=False,
            chain_type_kwargs={
                "prompt": promptTmp,
                "memory": memory_obj,
            }
        )

        try:
            result = cur_conversation({"query": user_prompt})
            response = format_response(result['result'])
            add_history(cur_conv, prompt, response["answer"])

        except Exception as e:
            save_error(e)
            return {
                "status": "error",
                "message": "Error while getting response",
                "conversation_id": str(cur_conv),
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
                "conversation_id": str(cur_conv)
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
    docsearch1 = Chroma(persist_directory="./db/866136357063950337", embedding_function=embeddings).as_retriever(
        search_kwargs={"k": 3})
    docsearch2 = Chroma(persist_directory="./db/866149744008953857", embedding_function=embeddings).as_retriever(
        search_kwargs={"k": 3})

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
                                                                   retriever=docsearch.as_retriever(
                                                                       search_kwargs={"k": 3}))

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
