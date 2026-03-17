from pydantic import BaseModel
from typing import List
from enum import Enum


# ----------------------------
# ROLE ENUM
# ----------------------------

class UserRole(str, Enum):
    Finance = "Finance"
    HR = "HR"
    Engineering = "Engineering"
    Marketing = "Marketing"
    CLevel = "C-Level"


# ----------------------------
# AUTH SCHEMAS
# ----------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ----------------------------
# CHAT SCHEMAS
# ----------------------------

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    documents_used: int
    response_time_ms: float
