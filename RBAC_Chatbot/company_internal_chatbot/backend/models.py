from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    query: str

class SourceDoc(BaseModel):
    document: str
    source: str
    roles: List[str]

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDoc]
