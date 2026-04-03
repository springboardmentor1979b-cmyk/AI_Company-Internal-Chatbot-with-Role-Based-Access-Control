from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    username:     str
    role:         str
    department:   str


class QueryRequest(BaseModel):
    question: str
    top_k:    int = 4


class QueryResponse(BaseModel):
    answer:      str
    sources:     list[str]
    chunks_used: int
    role:        str


class CreateUserRequest(BaseModel):
    username:   str
    password:   str
    role:       str
    department: str = ""
