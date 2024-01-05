import hashlib
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from cocroach_utils.db_assistants import get_all_assistants, get_assistant_by_id, update_assistant, add_assistant, \
    delete_assistant, update_assistant_field
from cocroach_utils.db_models import get_all_models, get_model_by_id, update_model, add_model, delete_model
from cocroach_utils.db_users import add_user, get_user_by_email, get_user_by_id, update_user, \
    update_user_field
from cocroach_utils.db_history import get_history_for_conv, update_history_field_by_id, delete_history_by_id
from cocroach_utils.db_conv import get_user_conversations, get_conv_by_id, \
    delete_conversation, \
    add_conversation, update_conversation_field
from cocroach_utils.db_docs import get_user_docs, get_all_docs, delete_doc_by_id, get_doc_by_id, update_doc_field_by_id
from models import ConvRequest, User, Conversation, History, Document, Model, Assistant
from utils.return_api import check_api_key, wrong_api, check_result, return_error, return_success
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
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Page not found"}


# RESPONSE ENDPOINTS
@app.post("/response/simple")
async def api_get_simple_response(body: ConvRequest):
    """
    :param body:
    :return:
    """
    if check_api_key(body.api_key) is False:
        return wrong_api()
    resp = get_simple_response(body.user_message, body.conversation_id, body.user_id, body.memory)
    return check_result(resp, 400, "No response")


@app.post("/response/doc")
async def api_get_doc_response(body: ConvRequest):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    resp = get_response_over_doc(body.user_message, body.conversation_id, body.document, body.user_id, body.memory)
    return check_result(resp, 400, "No response")



# CONVERSATIONS ENDPOINTS
@app.post("/conv/get")
async def api_get_conversation(body: Conversation):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.conv_id is not None:
        result = get_conv_by_id(body.conv_id)
    elif body.user_id is not None:
        result = get_user_conversations(body.user_id)
    else:
        return return_error(400, "conv_id or user_id is required")
    return check_result(result, 400, "Conversation do not exist")


@app.post("/conv/add")
async def api_add_conversation(body: Conversation):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.user_id is None:
        return return_error(400, "User conv_id is required")
    if body.title is None:
        return return_error(400, "Title is required")
    result = add_conversation(body.user_id, body.doc_id, body.title)
    return check_result(result, 400, "Cant create conversation")


@app.post("/conv/update_field")
async def api_update_conv(body: Conversation):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.conv_id is None:
        return return_error(400, "Conversation conv_id is required")
    if body.field is None:
        return return_error(400, "Conversation field is required")
    if body.value is None:
        return return_error(400, "Conversation value is required")
    result = update_conversation_field(body.conv_id, body.field, body.value)
    return check_result(result, 400, "Cant update conversation")


@app.post("/conv/delete")
async def api_delete_conv(body: Conversation):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    result = delete_conversation(body.conv_id)
    return check_result(result, 400, "Cant delete conversation")


# HISTORY ENDPOINTS
@app.post("/history/get")
async def api_get_history(body: Conversation):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    result = get_history_for_conv(body.conv_id, body.limit)
    return check_result(result, 400, "No history")


@app.post("history/delete")
async def api_delete_history(body: History):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    result = delete_history_by_id(body.hist_id)
    return check_result(result, 400, "Cant delete")


@app.post("/history/update_field")
async def api_history_update_field(body: History):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.hist_id is None:
        return return_error(400, "History conv_id is required")
    if body.field is None:
        return return_error(400, "History field is required")
    if body.value is None:
        return return_error(400, "History value is required")
    result = update_history_field_by_id(body.hist_id, body.field, body.value)
    return check_result(result, 400, "Cant update history")


# DOCS ENDPOINTS
@app.post("/docs/get")
async def api_get_docs(body: Document):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.doc_id is not None:
        result = get_doc_by_id(body.doc_id)
    elif body.user_id is not None:
        result = get_user_docs(body.user_id)
    else:
        result = get_all_docs()
    return check_result(result, 400, "No docs")


@app.post("/docs/add")
async def api_upload_file(file: UploadFile = File(...), user_id: int = Form(...), force: bool = Form(...),
                             api_key: str = Form(...)):
    if check_api_key(api_key) is False:
        return wrong_api()

    try:
        res = create_vector_index(file, user_id, force)
        if res['status'] == 'success':
            summary = get_doc_summary(file, str(res['data']['doc_id']))
            # TODO: make it as a common format for all return results
            return {
                "result": res,
                "summary": summary,
                "code": 200,
            }
        else:
            return return_success(res)
    except Exception as e:
        return return_error(400, str(e))


@app.post("/docs/update_field")
async def api_update_doc_field(body: Document):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.doc_id is None:
        return return_error(400, "Doc conv_id is required")
    if body.field is None:
        return return_error(400, "Doc field is required")
    if body.value is None:
        return return_error(400, "Doc value is required")
    result = update_doc_field_by_id(body.doc_id, body.field, body.value)
    return check_result(result, 400, "Cant update doc")


@app.post("/docs/delete")
async def api_delete_doc(body: Document):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.doc_id is not None:
        result = delete_doc_by_id(body.doc_id)
        return check_result(result, 400, "Cant delete doc")
    else:
        return return_error(400, "doc_id is required")


# USERS ENDPOINTS
@app.post("/user/login")
async def api_login_user(body: User):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    user = get_user_by_email(body.email)

    if len(user) == 0:
        return return_error(400, "User not found")

    if user['active'] == 0:
        return return_error(400, "User is not active")

    hs_function = hashlib.md5()
    hs_function.update(body.password.encode('utf-8'))
    password = hs_function.hexdigest()

    if user['password'] != password:
        return return_error(400, "Wrong password")
    return check_result(user, 400, "User not found")


@app.post("/user/get")
async def api_get_user(body: User):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    user = get_user_by_id(body.user_id)
    return check_result(user, 400, "User not found")


@app.post("/user/update")
async def api_update_user(body: User):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.user_id is None:
        return return_error(400, "User conv_id is required")
    if body.name is None:
        return return_error(400, "User name is required")
    if body.email is None:
        return return_error(400, "User email is required")
    result = update_user(body.user_id, body.name, body.email, body.password)
    return check_result(result, 400, "Cant update user")


@app.post("/user/update_field")
async def api_update_user_field(body: User):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.user_id is None:
        return return_error(400, "User conv_id is required")
    if body.field is None:
        return return_error(400, "User field is required")
    if body.value is None:
        return return_error(400, "User value is required")

    if body.field == 'password':
        # if we need to update user password
        user = get_user_by_id(body.user_id)
        psw = user['password']
        hs_function = hashlib.md5()
        hs_function.update(body.old_password.encode('utf-8'))
        old_password = hs_function.hexdigest()
        hs_function.update(body.value.encode('utf-8'))
        new_password = hs_function.hexdigest()

        if psw != old_password:
            return return_error(400, "Wrong password")
        result = update_user_field(body.user_id, 'password', new_password)
        return check_result(result, 400, "Cant update user")

    result = update_user_field(body.user_id, body.field, body.value)
    return check_result(result, 400, "Cant update user")


@app.post("/user/add")
async def api_add_user(body: User):
    if check_api_key(body.api_key) is False:
        return wrong_api()

    if body.name is None:
        return return_error(400, "Name is required")
    if body.email is None:
        return return_error(400, "Email is required")
    if body.password is None:
        return return_error(400, "Password is required")

    hs_function = hashlib.md5()
    hs_function.update(body.password.encode('utf-8'))
    password = hs_function.hexdigest()

    result = add_user(body.name, body.email, password)
    return check_result(result, 400, "Cant create user")


@app.post("/user/delete")
async def api_delete_user(body: User):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.user_id is None:
        return return_error(400, "User conv_id is required")
    result = update_user_field(body.user_id, 'active', 0)
    return check_result(result, 400, "Cant delete user")


# MODELS ENDPOINTS
@app.post("/models/get")
async def api_get_model(body: Model):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.model_id is not None:
        result = get_model_by_id(body.model_id)
    else:
        result = get_all_models()
    return check_result(result, 400, "No models")


@app.post("/models/update")
async def api_update_model(body: Model):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.model_id is None:
        return return_error(400, "Model conv_id is required")
    if body.name is None:
        return return_error(400, "Model name is required")
    if body.description is None:
        return return_error(400, "Model description is required")
    if body.price_in is None:
        return return_error(400, "Model price_in is required")
    if body.price_out is None:
        return return_error(400, "Model price_out is required")
    result = update_model(body.model_id, body.name, body.description, body.price_in, body.price_out)
    return check_result(result, 400, "Cant update model")

@app.post("/models/add")
async def api_add_model(body: Model):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.name is None:
        return return_error(400, "Model name is required")
    result = add_model(body.name, body.description, body.price_in, body.price_out)
    return check_result(result, 400, "Cant add model")


@app.post("/models/delete")
async def api_delete_model(body: Model):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.model_id is None:
        return return_error(400, "Model conv_id is required")
    result = delete_model(body.model_id)
    return check_result(result, 400, "Cant delete model")


# ASSISTANTS ENDPOINTS
@app.post("/assistant/get")
async def api_get_assistant(body: Assistant):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.assist_id is not None:
        result = get_assistant_by_id(body.assist_id)
    else:
        result = get_all_assistants()
    return check_result(result, 400, "No assistants")


@app.post("/assistant/update")
async def api_update_assistant(body: Assistant):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.assist_id is None:
        return return_error(400, "Assistant conv_id is required")
    if body.name is None:
        return return_error(400, "Assistant name is required")

    result = update_assistant(body.assist_id, body.name, body.description, body.welcome, body.prompt, body.user)
    return check_result(result, 400, "Cant update assistant")


@app.post("/assistant/update_field")
async def api_update_assistant_field(body: Assistant):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.assist_id is None:
        return return_error(400, "Assistant conv_id is required")
    if body.field is None:
        return return_error(400, "Assistant field is required")
    if body.value is None:
        return return_error(400, "Assistant value is required")
    result = update_assistant_field(body.assist_id, body.field, body.value)
    return check_result(result, 400, "Cant update assistant")


@app.post("/assistant/add")
async def api_add_assistant(body: Assistant):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.name is None:
        return return_error(400, "Assistant name is required")
    result = add_assistant(body.name, body.description, body.welcome, body.prompt, body.user)
    return check_result(result, 400, "Cant add assistant")


@app.post("/assistant/delete")
async def api_delete_assistant(body: Assistant):
    if check_api_key(body.api_key) is False:
        return wrong_api()
    if body.assist_id is None:
        return return_error(400, "Assistant conv_id is required")
    result = delete_assistant(body.assist_id)
    return check_result(result, 400, "Cant delete assistant")
