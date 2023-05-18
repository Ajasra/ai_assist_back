import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredEPubLoader, UnstructuredWordDocumentLoader, \
    UnstructuredFileLoader

from cocroach_utils.db_errors import save_error
from cocroach_utils.db_docs import add_doc, get_doc_by_name

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

    try:
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
    except Exception as e:
        save_error(e)
        return None


def create_vector_index(file, user_id, force):
    """
    Create a vector index from a file
    :param file:
    :return:
    """

    if file.filename == '':
        return {
            "status": "error",
            "message": "No file selected"
        }

    filename = f"./data/{file.filename}"

    docs = get_doc_by_name(file.filename)
    if not force:
        if docs:
            return {
                    "status": "error",
                    "message": "File already exists"
            }

    if not docs:
        doc_id = add_doc(user_id, file.filename, "")
    else:
        doc_id = docs[0][0]

    save_directory = os.path.join(persist_directory, str(doc_id))
    with open(Path(filename), "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    if not os.path.exists(os.path.join(save_directory, 'index')) or force:

        loader = get_loader(filename)
        if loader is None:
            return {
                "status": "error",
                "message": "File format is not supported"
            }

        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_documents(documents)

        try:
            embedding = OpenAIEmbeddings()
            vectordb = Chroma.from_documents(documents=docs, embedding=embedding, persist_directory=save_directory)
            vectordb.persist()
        except Exception as e:
            save_error(e)
            return {
                "status": "error",
                "message": "Error creating index",
                "error": str(e)
            }

        return {
            "status": "success",
            "message": "Index created successfully",
            "data": {
                "filename": filename,
                "save_directory": save_directory,
                "doc_id": str(doc_id)
            }
        }

    else:
        return {
            "status": "success",
            "message": "Index already exists",
            "data": {
                "filename": filename,
                "save_directory": save_directory,
                "doc_id": str(doc_id)
            }
        }
