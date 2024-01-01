from pydantic import BaseModel
from fastapi import UploadFile, File, Form


class ConvRequest(BaseModel):
    user_message: str
    conversation_id: int = None
    user_id: int = None
    document: int = None
    memory: int = 10
    api_key: str = "null"


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


class DocRequest(BaseModel):
    file: UploadFile = File(...)
    user_id: int = Form(...)
    force: bool = Form(...)


class Document(BaseModel):
    doc_id: int = None
    api_key: str = None


class History(BaseModel):
    hist_id: int = None
    feedback: int = 0
    api_key: str = None
