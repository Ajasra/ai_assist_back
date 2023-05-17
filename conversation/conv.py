import os
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain

from cocroach_utils.database_utils import save_error

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


def get_agent_response(prompt, conversation_id, document, debug):
    if document is not None:

        cur_conversation = None

        index_dir = os.path.join(persist_directory, document)
        embeddings = OpenAIEmbeddings()
        docsearch = Chroma(persist_directory=index_dir, embedding_function=embeddings)

        _DEFAULT_TEMPLATE = """Given the context information answer the following question
                            If you don't know the answer, just say you dont know Don't try to make up an answer.
                            =========
                            Always answer in the format:
                            ANSWER: <your answer>
                            FOLLOW UP QUESTIONS: <list of 3 suggested questions related to context and conversation for better understanding>
                            SOURCE: <do not make up source, give the page or the chapter from the document>
                            =========
                            question: {}""".format(prompt)

        if conversation_id >= len(conversations) or len(conversations) == 0:
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            memories.append(memory)

            conversations.append(
                RetrievalQAWithSourcesChain.from_chain_type(llm=llm,chain_type="stuff",retriever=docsearch.as_retriever())
            )
            conversation_id = len(conversations) - 1
            cur_conversation = conversations[conversation_id]
        else:
            cur_conversation = conversations[conversation_id]

        try:
            result = cur_conversation({"question": _DEFAULT_TEMPLATE})
            response = format_response(result["answer"])
        except Exception as e:
            save_error(e)
            return {
                "status": "error",
                "message": "Error while getting response",
                "conversation_id": conversation_id,
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
                "conversation_id": conversation_id
            }
        }

    else:
        save_error("No document selected")
        return {
            "status": "error",
            "message": "No document selected",
            "conversation_id": conversation_id
        }


def get_conversation_count():
    """Get conversation count.

    Returns:
        int: Conversation count.
    """
    return len(conversations)
