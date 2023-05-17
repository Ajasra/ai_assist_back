import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from cocroach_utils.database_utils import save_error

load_dotenv()


def get_file_summary(persist_dir):
    """
    Get the summary of the file
    :return:
    """

    embeddings = OpenAIEmbeddings()
    docsearch = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    chain = RetrievalQAWithSourcesChain.from_chain_type(ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
                                                        chain_type="stuff", retriever=docsearch.as_retriever())
    prompt_template = "Give me an extensive summary of the document. Try to include details from the document as a a " \
                      "main ideas and concepts. \n"
    try:

        result = chain({"question": prompt_template}, return_only_outputs=True)
        with open(os.path.join(persist_dir, "summary.txt"), "w") as f:
            f.write(result["answer"])
        return {
            "status": "success",
            "message": "File summary",
            "data": {
                "summary": result["answer"]
            }
        }

    except Exception as e:

        save_error(e)
        return {
            "status": "error",
            "message": "Error in getting summary",

        }
