from pydantic import BaseModel
from pathlib import Path
import shutil
from fastapi import FastAPI, UploadFile, File

from vectordb.vectordb import create_vector_index, get_file_summary
from conversation.conv import get_agent_response

app = FastAPI()
debug = True


class ConvRequest(BaseModel):
    user_message: str
    conversation_id: int = 0


class UserId(BaseModel):
    user_id: int = 0


@app.get("/")
def read_root():
    return {"Page not found"}


# CONVERSATIONS
@app.post("/conv/get_response")
async def get_response(body: ConvRequest):

    resp = get_agent_response(body.user_message, body.conversation_id, debug)

    return {
        "response": resp,
        "debug": debug,
        "code": 200,
        "conversation_id": 0
    }


@app.post("/conv/get_suggestion")
async def get_suggestion(body: ConvRequest):

    return {
        "response": "response message",
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/get_user_conversations")
async def get_user_conversation(body: UserId):

    return {
        "response": body.user_id,
        "debug": debug,
        "code": 200,
    }


@app.post("/conv/get_selected_conv")
async def get_selected_conv(conversation_id):

    return {
        "response": "response message",
        "debug": debug,
        "code": 200,
    }



# INDEXES
@app.post("/docs/get_indexes")
async def get_indexes():

    return {
        "response": "response message",
        "debug": debug,
        "code": 200,
    }



# FILES
@app.post("/docs/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):

    res = create_vector_index(file)
    res2 = None
    if res['data']['save_directory'] is not None:
        res2 = get_file_summary(res['data']['save_directory'])

    return {
        "result": res,
        "summary": res2,
        "code" : 200,
    }