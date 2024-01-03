import hashlib
import os.path
from dotenv import load_dotenv

from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from cocroach_utils.db_models import get_all_models, get_model_by_id
from cocroach_utils.db_users import add_user, get_user_by_email, get_user_by_id, update_user, get_user_password
from cocroach_utils.db_history import get_history_for_conv, update_history_feedback_by_id
from cocroach_utils.db_conv import get_user_conversations, get_conv_by_id, update_conversation_title, \
    delete_conversation, \
    add_conversation, update_conversation_active, update_conversation_summary, update_conversation_field
from cocroach_utils.db_docs import update_doc_summary_by_id, get_user_docs, get_all_docs, delete_doc_by_id
from vectordb.vectordb import create_vector_index
from conversation.conv import get_response_over_doc, get_simple_response, get_doc_summary


load_dotenv()
app = FastAPI()
debug = True

origins = [
    "http://localhost.com",
    "https://localhost.com",
    "http://localhost",
    "http://localhost:3001",
    "http://sokaris.link:3001",
    "http://sokaris.link",
    "http://assistant.sokaris.link",
    "https://fr.sokaris.link",
    "http://fr.sokaris.link",
    "https://localhost:3001",
    "http://fr.sokaris.link",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# default values for start
usr_id = 0


class ConvRequest(BaseModel):
    user_message: str
    conversation_id: int = None
    user_id: int = None
    document: int = None
    memory: int = 10
    api_key: str = None


class User(BaseModel):
    user_id: int = 0
    name: str = None
    email: str = None
    password: str = None
    old_password: str = None
    hash_password: str = None
    api_key: str = None


class Conversation(BaseModel):
    conv_id: int = 0
    limit: int = 10
    title: str = None
    user_id: int = None
    doc_id: int = None
    active: bool = None
    summary: str = None
    api_key: str = None
    model: str = None
    assistant: str = None


class DocRequest(BaseModel):
    file: UploadFile = File(...)
    user_id: int = Form(...)
    force: bool = Form(...)


class EmptyRequest(BaseModel):
    api_key: str = None


class Model(BaseModel):
    api_key: str = None
    model_id: int = 0
    model_name: str = ""
    model_description: str = ""
    model_price_in: float = 0
    model_price_out: float = 0


class Document(BaseModel):
    doc_id: int = None
    api_key: str = None


class History(BaseModel):
    hist_id: int = None
    feedback: int = 0
    api_key: str = None



def check_api_key(api_key):
    print(api_key)
    print(os.getenv("PUBLIC_API_KEY"))
    if api_key is None:
        return False
    if api_key == os.getenv("PUBLIC_API_KEY"):
        return True
    return False


@app.get("/")
def read_root():
    return {"Page not found"}


# CONVERSATIONS
@app.post("/conv/get_response")
async def get_response(body: ConvRequest):
    """
    :param body:
    :return:
    """

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    resp = get_simple_response(body.user_message, body.conversation_id, body.user_id, body.memory)

    return {
        "response": resp,
        "debug": debug,
        "code": 200
    }


@app.post("/conv/get_response_doc")
async def get_response(body: ConvRequest):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    resp = get_response_over_doc(body.user_message, body.conversation_id, body.document, body.user_id, body.memory)

    return {
        "response": resp,
        "debug": debug,
        "code": 200
    }


@app.post("/conv/get_user_conversations")
async def get_user_conversation(body: User):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    result = get_user_conversations(body.user_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/get_selected_conv")
async def get_selected_conv(body: Conversation):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    result = get_conv_by_id(body.conv_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


# HISTORY
@app.post("/conv/get_history")
async def get_history(body: Conversation):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    result = get_history_for_conv(body.conv_id, body.limit)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/create")
async def create_conv(body: Conversation):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    if body.user_id is None:
        return {
            "response": "User ID is required",
            "code": 400,
        }

    if body.title is None:
        return {
            "response": "Title is required",
            "code": 400,
        }

    result = add_conversation(body.user_id, body.doc_id, body.title)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/history/feedback")
async def history_feedback(body: History):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    if body.hist_id is None:
        return {
            "response": "History ID is required",
            "code": 400,
        }

    result = update_history_feedback_by_id(body.hist_id, body.feedback)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/update")
async def update_conv_title(body: Conversation):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    if body.title is not None:
        result = update_conversation_field(body.conv_id, 'title', body.title)
    elif body.active is not None:
        result = update_conversation_field(body.conv_id, 'acttive', body.active)
    elif body.summary is not None:
        result = update_conversation_field(body.conv_id, 'summary', body.summary)
    elif body.model is not None:
        result = update_conversation_field(body.conv_id, 'model', body.model)
    elif body.assistant is not None:
        result = update_conversation_field(body.conv_id, 'assistant', body.assistant)
    else:
        return {
            "response": "No data to update",
            "code": 400,
        }

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/delete")
async def delete_conv(body: Conversation):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    result = delete_conversation(body.conv_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


# DOCS
@app.post("/docs/get_docs/user_id")
async def get_indexes(body: User):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    try:
        if body.user_id == 0:
            docs = get_all_docs()
        else:
            docs = get_user_docs(body.user_id)
    except Exception as e:
        return {
            "response": "Cant get docs",
            "code": 400,
        }

    return {
        "response": docs,
        "debug": debug,
        "code": 200,
    }


@app.post("/docs/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), user_id: int = Form(...), force: bool = Form(...), api_key: str = Form(...)):

    if check_api_key(api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    try:
        res = create_vector_index(file, user_id, force)
        print('Uploading')

        if res['status'] == 'success':
            summary = get_doc_summary(file, str(res['data']['doc_id']))

            return {
                "result": res,
                "summary": summary,
                "code": 200,
            }

        else:
            return {
                "result": res,
                "code": 400,
            }
    except Exception as e:
        return {
            "result": str(e),
            "code": 400,
        }


@app.post("/docs/delete")
async def delete_doc(body: Document):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    if body.doc_id is not None:
        try:
            res = delete_doc_by_id(body.doc_id)

            return {
                "result": res,
                "code": 200,
            }
        except Exception as e:
            return {
                "result": str(e),
                "code": 400,
            }
    else:
        return {
            "result": "doc_id is required",
            "code": 400,
        }


# USERS
@app.post("/user/create")
async def create_user(body: User):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    if body.name is None:
        return {
            "response": "Name is required",
            "code": 400,
        }
    if body.email is None:
        return {
            "response": "Email is required",
            "code": 400,
        }
    if body.password is None:
        return {
            "response": "Password is required",
            "code": 400,
        }

    # create hash for password
    hs_function = hashlib.md5()
    password = hs_function.update(body.password.encode('utf-8'))
    password = hs_function.hexdigest()

    try:
        result = add_user(body.name, body.email, password)
        if result == -1:
            return {
                "response": "User already exists",
                "code": 400,
            }
    except Exception as e:
        return {
            "response": str(e),
            "code": 400,
        }

    return {
        "user_id": result,
        "code": 200,
    }


@app.post("/user/login")
async def login_user(body: User):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    user = get_user_by_email(body.email)

    if len(user) == 0:
        return {
            "response": "User not found",
            "code": 400,
        }

    if user['active'] == 0:
        return {
            "response": "User is not active",
            "code": 400,
        }

    hs_function = hashlib.md5()
    password = hs_function.update(body.password.encode('utf-8'))
    password = hs_function.hexdigest()

    if user['password'] != password:
        return {
            "response": "Wrong password",
            "code": 400,
        }

    return {
        "data": {
            "user_id": user['user_id'],
            "name": user['name'],
            "email": user['email'],
            "password": user['password'],
            "role": user['role']
        },
        "code": 200,
    }


@app.post("/user/get_user")
async def get_user(body: User):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    user = get_user_by_id(body.user_id)

    return {
        "data": user,
        "code": 200,
    }


@app.post("/user/update_user_password")
async def update_user_password(body: User):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    user = get_user_by_id(body.user_id)
    psw = get_user_password(body.user_id)
    hs_function = hashlib.md5()
    old_password = hs_function.update(body.old_password.encode('utf-8'))
    old_password = hs_function.hexdigest()

    new_password = hs_function.update(body.password.encode('utf-8'))
    new_password = hs_function.hexdigest()

    if psw != old_password:
        return {
            "response": "Wrong password",
            "code": 400,
        }

    result = update_user(body.user_id, user['name'], user['email'], new_password)

    return {
        "status": "success",
        "data": result,
        "code": 200,
    }


@app.post("/models/get_models")
async def get_models(body: Model):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    models = get_all_models()

    return {
        "status": "success",
        "response": models,
        "code": 200,
    }


@app.post("/models/get_model_by_id")
async def get_model_id(body: Model):

    if check_api_key(body.api_key) is False:
        return {
            "response": "Invalid API Key",
            "code": 400,
        }

    model = get_model_by_id(body.model_id)

    return {
        "status": "success",
        "response": model,
        "code": 200,
    }

