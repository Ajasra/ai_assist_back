from fastapi import UploadFile, File, Form
from pydantic import BaseModel


class ConvRequest(BaseModel):
    """Conversation request model"""
    api_key: str = None
    user_id: int = None
    conversation_id: int = None
    user_message: str
    document: int = None
    memory: int = 10


class User(BaseModel):
    """User model"""
    api_key: str = None
    user_id: int = 0
    name: str = None
    email: str = None
    password: str = None
    old_password: str = None
    hash_password: str = None
    active: bool = None
    field: str = None
    value: str = None


class Conversation(BaseModel):
    """Conversation model"""
    api_key: str = None
    conv_id: int = None
    title: str = None
    user_id: int = None
    doc_id: int = None
    active: bool = None
    summary: str = None
    model: str = None
    assistant: str = None
    limit: int = 10
    field: str = None
    value: str = None


class DocRequest(BaseModel):
    """Document request model"""
    file: UploadFile = File(...)
    user_id: int = Form(...)
    force: bool = Form(...)


class EmptyRequest(BaseModel):
    """Empty request model"""
    api_key: str = None


class Document(BaseModel):
    """Document model"""
    api_key: str = None
    doc_id: int = None
    user_id: int = None
    name: str = None
    summary: str = None
    updated: str = None
    active: bool = None
    field: str = None
    value: str = None


class History(BaseModel):
    """History model"""
    api_key: str = None
    hist_id: int = None
    conv_id: int = None
    prompt: str = None
    answer: str = None
    feedback: int = None
    followup: str = None
    field: str = None
    value: str = None


class Model(BaseModel):
    """Models model"""
    api_key: str = None
    model_id: int = None
    name: str = ""
    description: str = ""
    price_in: float = 0
    price_out: float = 0
    field: str = None
    value: str = None


class Assistant(BaseModel):
    """Assistant model"""
    api_key: str = None
    assist_id: int = None
    name: str = ""
    description: str = ""
    welcome: str = ""
    system_prompt: str = ""
    user_id: int = 0
    field: str = None
    value: str = None
