from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()
debug = True


class ConvRequest(BaseModel):
    user_message: str
    conversation_id: int = 0
    assistant_id: int = 0
    memory_type: int = 0


@app.get("/")
def read_root():
    return {"Page not found"}


@app.post("/conv/assistant")
async def assistant(body: ConvRequest):
    """
    Main conversation endpoint.
    :param body:
    :return:
    """

    return {
        "response": "response message",
        "debug": debug,
        "code": 200,
        "conversation_id": 0
    }


@app.post("/conv/suggestion")
async def suggestion(body: ConvRequest):
    """
    Return suggestion for the current conversation
    :param body:
    :return:
    """

    return {
        "response": "response message",
        "debug": debug,
        "code": 200,
        "conversation_id": 0
    }
