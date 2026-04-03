from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from contextlib import asynccontextmanager

from backend.database import init_db, get_db_connection
from backend.auth import verify_password, create_access_token
from backend.rbac import get_current_user
from backend.rag import init_rag_db, get_answer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the DBs
    init_db()
    init_rag_db()
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan, title="Company Internal Chatbot API")

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: str

@app.post("/login", response_model=Token)
def login(request: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (request.username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Verify password
    # in a real scenario: verify_password(request.password, user["password_hash"])
    # in this dummy scenario, we just check if it's correct.
    if not verify_password(request.password, user["password_hash"]):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_role = current_user["role"]
    query = request.query
    
    # Process through RAG
    result = get_answer(query, user_role)
    
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"]
    )
