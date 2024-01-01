import hashlib
import os

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Union

from app import app

from cocroach_utils.db_conv import get_conv_by_id, add_conversation, update_conversation_title, \
    update_conversation_active, update_conversation_summary, delete_conversation
from cocroach_utils.db_docs import get_all_docs, get_user_docs, delete_doc_by_id
from cocroach_utils.db_history import get_history_for_conv, update_history_feedback_by_id
from cocroach_utils.db_users import add_user, get_user_by_email, get_user_by_id, get_user_password, update_user
from models import ConvRequest, User, Conversation, Document, History
from conversation.conv import get_response_over_doc, get_simple_response, get_doc_summary
from vectordb.vectordb import create_vector_index

debug = True
router = APIRouter()


def check_api_key(api_key: str) -> bool:
    """
    Check if the provided API key is valid.

    :param api_key: The API key to check.
    :return: True if the API key is valid, False otherwise.
    """
    if api_key is None:
        return False
    if api_key == os.getenv("PUBLIC_API_KEY"):
        return True
    return False


def validate_api_key(api_key: str) -> None:
    """
    Validate the provided API key. If the API key is not valid, raise an HTTPException.

    :param api_key: The API key to validate.
    """
    if not check_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API Key")


@router.post("/conv/get_response")
async def get_response(body: ConvRequest) -> dict:
    """
    Get a response.

    :param body: The request body.
    :return: The response.
    """
    validate_api_key(body.api_key)
    resp = await get_simple_response(body.user_message, body.conversation_id, body.user_id, body.memory)
    return {
        "response": resp,
        "debug": debug,
        "code": 200
    }


@router.post("/conv/get_response_doc")
async def get_response_doc(body: ConvRequest):
    validate_api_key(body.api_key)
    resp = await get_response_over_doc(body.user_message, body.conversation_id, body.document, body.user_id, body.memory)

    return {
        "response": resp,
        "debug": debug,
        "code": 200
    }


@router.post("/conv/get_user_conversations")
async def get_user_conversations(body: User):
    validate_api_key(body.api_key)

    result = await get_user_conversations(body.user_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@router.post("/conv/get_selected_conv")
async def get_selected_conv(body: Conversation):
    validate_api_key(body.api_key)

    result = await get_conv_by_id(body.conv_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@router.post("/conv/get_history")
async def get_history(body: Conversation):
    validate_api_key(body.api_key)

    result = await get_history_for_conv(body.conv_id, body.limit)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@router.post("/conv/create")
async def create_conv(body: Conversation):
    validate_api_key(body.api_key)

    if body.user_id is None:
        return {
            "response": "User ID is required",
            "code": 400,
        }

    if body.doc_id is None:
        return {
            "response": "Document ID is required",
            "code": 400,
        }

    if body.title is None:
        return {
            "response": "Title is required",
            "code": 400,
        }

    result = await add_conversation(body.user_id, body.doc_id, body.title)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@router.post("/conv/history/feedback")
async def history_feedback(body: History):
    validate_api_key(body.api_key)

    if body.hist_id is None:
        return {
            "response": "History ID is required",
            "code": 400,
        }

    result = await update_history_feedback_by_id(body.hist_id, body.feedback)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@router.post("/conv/update")
async def update_conv_title(body: Conversation):
    validate_api_key(body.api_key)

    if body.title is not None:
        result = await update_conversation_title(body.conv_id, body.title)
    elif body.active is not None:
        result = await update_conversation_active(body.conv_id, body.active)
    elif body.summary is not None:
        result = await update_conversation_summary(body.conv_id, body.summary)
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


@router.post("/conv/delete")
async def delete_conv(body: Conversation):
    validate_api_key(body.api_key)

    result = await delete_conversation(body.conv_id)

    return {
        "response": result,
        "debug": debug,
        "code": 200,
    }


@router.post("/docs/get_docs/user_id")
async def get_indexes(body: User):
    validate_api_key(body.api_key)

    try:
        if body.user_id == 0:
            docs = await get_all_docs()
        else:
            docs = await get_user_docs(body.user_id)
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


@router.post("/docs/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), user_id: int = Form(...), force: bool = Form(...),
                             api_key: str = Form(...)):
    validate_api_key(api_key)

    try:
        res = await create_vector_index(file, user_id, force)
        print('Uploading')

        if res['status'] == 'success':
            summary = await get_doc_summary(file, str(res['data']['doc_id']))

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


@router.post("/docs/delete")
async def delete_doc(body: Document):
    validate_api_key(body.api_key)

    if body.doc_id is not None:
        try:
            res = await delete_doc_by_id(body.doc_id)

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


@router.post("/user/create")
async def create_user(body: User):
    validate_api_key(body.api_key)

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
    hs_function.update(body.password.encode('utf-8'))
    password = hs_function.hexdigest()

    try:
        result = await add_user(body.name, body.email, password)
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


@router.post("/user/login")
async def login_user(body: User):
    validate_api_key(body.api_key)

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
    hs_function.update(body.password.encode('utf-8'))
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


@router.post("/user/get_user")
async def get_user(body: User):
    validate_api_key(body.api_key)

    user = get_user_by_id(body.user_id)

    return {
        "data": user,
        "code": 200,
    }


@router.post("/user/update_user_password")
async def update_user_password(body: User):
    validate_api_key(body.api_key)

    user = await get_user_by_id(body.user_id)
    psw = await get_user_password(body.user_id)
    hs_function = hashlib.md5()
    hs_function.update(body.old_password.encode('utf-8'))
    old_password = hs_function.hexdigest()

    hs_function.update(body.password.encode('utf-8'))
    new_password = hs_function.hexdigest()

    if psw != old_password:
        return {
            "response": "Wrong password",
            "code": 400,
        }

    result = await update_user(body.user_id, user['name'], user['email'], new_password)

    return {
        "status": "success",
        "data": result,
        "code": 200,
    }


app.include_router(router)
