from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import users_db
from auth import create_token
from rag import query_rag

app = FastAPI()

class Login(BaseModel):
    username: str
    password: str

class Query(BaseModel):
    question: str
    role: str

@app.post("/login")
def login(data: Login):
    user = users_db.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(data.username, user["role"])
    return {"token": token, "role": user["role"]}

@app.post("/chat")
def chat(q: Query):
    response = query_rag(q.question, q.role)
    return {"response": response}