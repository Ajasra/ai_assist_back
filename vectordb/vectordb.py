import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredEPubLoader, UnstructuredWordDocumentLoader, \
    UnstructuredFileLoader
from langchain.document_loaders import DirectoryLoader

from cocroach_utils.db_errors import save_error
from cocroach_utils.db_docs import add_doc, get_doc_by_name

# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.embeddings import HuggingFaceInstructEmbeddings

load_dotenv()
openai_api = os.environ.get("OPENAI_API_KEY")

# instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl",
#                                                       model_kwargs={"device": "cpu"})

chunk_size = 512
chunk_overlap = 32
persist_directory = './db'
data_directory = './data'
local_embeddings = False


# if local_embeddings:
#     model_name = "sentence-transformers/all-mpnet-base-v2"
#     hf = HuggingFaceEmbeddings(model_name=model_name)



# check if directory exists
if not os.path.exists(data_directory):
    os.makedirs(data_directory)
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)


def get_embedding_model(local=False):
    """
    Get the embedding model
    :param local:
    :return:
    """
    return OpenAIEmbeddings()
    # if local:
    #     return instructor_embeddings
    # else:
    #     return OpenAIEmbeddings()


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
    :param force:
    :param user_id:
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
        doc_id = docs['doc_id']

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
        # text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                          encoding_name="cl100k_base")
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


def create_vector_index_folder():

    data_directory = './data/summary'

    save_directory = os.path.join(persist_directory, 'summary')
    loader = DirectoryLoader(data_directory)
    documents = loader.load()
    print(len(documents))

    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)

    embedding = get_embedding_model()
    vectordb = Chroma.from_documents(documents=docs, embedding=embedding, persist_directory=save_directory)
    vectordb.persist()