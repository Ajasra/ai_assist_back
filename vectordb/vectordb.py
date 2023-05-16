import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredEPubLoader, UnstructuredWordDocumentLoader, \
    UnstructuredFileLoader


load_dotenv()
openai_api = os.environ.get("OPENAI_API_KEY")


chunk_size = 1000
chunk_overlap = 100

persist_directory = './db'
data_directory = './data'

# check if directory exists
if not os.path.exists(data_directory):
    os.makedirs(data_directory)
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)


def get_loader(filename):
    """
    Get the appropriate loader for the file type
    :param filename:
    :return:
    """
    if filename.endswith('.txt'):
        return TextLoader(filename)
    elif filename.endswith('.pdf'):
        return PyPDFLoader(filename)
    elif filename.endswith('.epub'):
        return UnstructuredEPubLoader(filename)
    elif filename.endswith('.docx') or filename.endswith('.doc'):
        return UnstructuredWordDocumentLoader(filename)
    else:
        return None


def get_file_summary(persist_dir):
    """
    Get the summary of the file
    :return:
    """
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    chain = RetrievalQAWithSourcesChain.from_chain_type(ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"), chain_type="stuff",
                                                        retriever=docsearch.as_retriever())

    prompt_template = "Give me an extensive summary of the document. Try to include details from the document as a a main ideas and concepts. \n"
    result = chain({"question": prompt_template}, return_only_outputs=True)
    print("Answer: " + result["answer"].replace('\n', ' '))
    print("Source: " + result["sources"])

    # save this to a file
    with open(os.path.join(persist_dir,"summary.txt"), "w") as f:
        f.write(result["answer"])

    return {
        "status": "success",
        "message": "File summary",
        "data": {
            "summary": result["answer"]
        }
    }


def create_vector_index(file):
    """
    Create a vector index from a file
    :param file:
    :return:
    """
    filename = f"./data/{file.filename}"
    save_directory = os.path.join(persist_directory, filename.split("/")[-1].split(".")[0])
    with open(Path(filename), "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    if not os.path.exists(os.path.join(save_directory, 'index')):

        loader = get_loader(filename)
        if loader is None:
            return {
                "status": "error",
                "message": "File format is not supported"
            }

        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_documents(documents)

        embedding = OpenAIEmbeddings()

        vectordb = Chroma.from_documents(documents=docs, embedding=embedding, persist_directory=save_directory)
        vectordb.persist()

        return {
            "status": "success",
            "message": "Index created successfully",
            "data": {
                "filename": filename,
                "save_directory": save_directory
            }
        }

    else:
        return {
            "status": "error",
            "message": "Index already exists",
            "data": {
                "filename": filename,
                "save_directory": save_directory
            }
        }
