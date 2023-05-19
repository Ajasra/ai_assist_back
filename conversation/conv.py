import os
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
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

    data = response_input.split("FOLLOW UP QUESTIONS:")
    if len(data) > 1:
        answer = data[0].strip()
        data = data[1].split("SOURCE")
        follow_up_questions = data[0].replace("FOLLOWUP QUESTIONS:","").strip().split("\n")
        source = data[1].replace("SOURCE:","").strip()
        return {
            "answer": answer,
            "follow_up_questions": follow_up_questions,
            "source": source
        }

    else:
        return {
            "answer": response_input,
            "follow_up_questions": [],
            "source": ""
        }


def get_agent_response(prompt, conv_id, doc_id, user_id, debug):
    if doc_id is not None:

        index_dir = os.path.join(persist_directory, str(doc_id))
        embeddings = OpenAIEmbeddings()
        docsearch = Chroma(persist_directory=index_dir, embedding_function=embeddings)

        cur_conv = None

        if conv_id is None or conv_id == -1 or conv_id == 0:
            cur_conv = add_conversation(user_id, doc_id, title="New conversation")
            print("New conversation added"
                  "Conversation id: ", cur_conv)
        else:
            conv = get_conv_by_id(conv_id)
            if conv is None:
                save_error("Conversation not found")
                return {
                    "status": "error",
                    "message": "Conversation not found",
                    "conversation_id": conv_id
                }
            else:
                cur_conv = conv_id

        if cur_conv == -1:
            save_error("Error while adding conversation")
            return {
                "status": "error",
                "message": "Error while adding conversation",
                "conversation_id": cur_conv
            }

        _DEFAULT_TEMPLATE = """Given the context information answer the following question
                            If you don't know the answer, just say you dont know Don't try to make up an answer.
                            =========
                            Always answer in the format:
                            ANSWER: <your answer>
                            FOLLOW UP QUESTIONS: <list of 3 suggested questions related to context and conversation for better understanding>
                            SOURCE: <do not make up source, give the page or the chapter from the document>
                            =========
                            question: {}""".format(prompt)

        cur_conversation = RetrievalQAWithSourcesChain.from_chain_type(llm=llm,chain_type="stuff",retriever=docsearch.as_retriever())

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
                "source": response["source"],
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

def multichain():
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