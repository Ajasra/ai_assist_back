import hashlib
import os.path

from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from cocroach_utils.db_users import add_user, get_user_by_email, get_user_by_id, update_user, get_user_password
from cocroach_utils.db_history import get_history_for_conv
from cocroach_utils.db_conv import get_user_conversations, get_conv_by_id, update_conversation, delete_conversation
from cocroach_utils.db_docs import update_doc_summary_by_id, get_user_docs, get_all_docs
from conversation.requests_conv import get_file_summary
from vectordb.vectordb import create_vector_index
from conversation.conv import get_response_over_doc, get_simple_response

app = FastAPI()
debug = True

origins = [
    "http://localhost.com",
    "https://localhost.com",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# default values for start
usr_id = 0


class ConvRequest(BaseModel):
    user_message: str
    conversation_id: int = None
    user_id: int = None
    document: int = None
    memory: dict = None


class User(BaseModel):
    user_id: int = 0
    name: str = None
    email: str = None
    password: str = None
    old_password: str = None
    hash_password: str = None


class Conversation(BaseModel):
    conv_id: int = 0
    limit: int = 10
    title: str = None


class DocRequest(BaseModel):
    file: UploadFile = File(...)
    user_id: int = Form(...)
    force: bool = Form(...)


@app.get("/")
def read_root():
    return {"Page not found"}


# CONVERSATIONS
@app.post("/conv/get_response")
async def get_response(body: ConvRequest):
    resp = get_simple_response(body.user_message, body.conversation_id, body.user_id, body.memory)

    return {
        "response": resp,
        "debug": debug,
        "code": 200
    }


@app.post("/conv/get_response_doc")
async def get_response(body: ConvRequest):
    resp = get_response_over_doc(body.user_message, body.conversation_id, body.document, body.user_id, body.memory)

    return {
        "response": resp,
        "debug": debug,
        "code": 200
    }


@app.post("/conv/get_user_conversations")
async def get_user_conversation(body: User):
    result = get_user_conversations(body.user_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/get_selected_conv")
async def get_selected_conv(body: Conversation):
    result = get_conv_by_id(body.conv_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


# HISTORY
@app.post("/conv/get_history")
async def get_history(body: Conversation):
    result = get_history_for_conv(body.conv_id, body.limit)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }

@app.post("/conv/update")
async def update_conv(body: Conversation):

    if body.title is None:
        return {
            "response": "Title is required",
            "code": 400,
        }
    result = update_conversation(body.conv_id, body.title)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/delete")
async def delete_conv(body: Conversation):
    result = delete_conversation(body.conv_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


# DOCS
@app.post("/docs/get_docs/user_id")
async def get_indexes(body: User):
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
async def create_upload_file(file: UploadFile = File(...), user_id: int = Form(...), force: bool = Form(...)):

    res = create_vector_index(file, user_id, force)
    print('Uploading')

    if res['status'] == 'success':
        summary = get_file_summary(os.path.join("./db", str(res['data']['doc_id'])))
        if summary['status'] == 'success':
            update_doc_summary_by_id(res['data']['doc_id'], summary['data']['summary'])

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


# USERS
@app.post("/user/create")
async def create_user(body: User):
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
    user = get_user_by_email(body.email)
    print(user)

    if len(user) == 0:
        return {
            "response": "User not found",
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
            "password": user['password']
        },
        "code": 200,
    }


@app.post("/user/get_user")
async def get_user(body: User):
    user = get_user_by_id(body.user_id)

    return {
        "data": user,
        "code": 200,
    }


@app.post("/user/update_user_password")
async def update_user_password(body: User):
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
