from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import uvicorn
from contextlib import asynccontextmanager

from db import init_db, get_db_connection
from models import UserCreate, Token, ChatRequest, ChatResponse
from auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from rbac import get_current_active_user
from rag import load_documents, retrieve_and_generate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        load_documents()
        print("Documents loaded successfully into ChromaDB")
    except Exception as e:
        print(f"Error loading documents: {e}")
    yield

app = FastAPI(title="Internal Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM users WHERE username = ?", (user.username,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = get_password_hash(user.password)
    conn.execute(
        "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
        (user.username, hashed_pw, user.role.lower())
    )
    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (form_data.username,)).fetchone()
    conn.close()
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, current_user: dict = Depends(get_current_active_user)):
    user_role = current_user["role"].lower()
    query = request.query
    
    response_data = retrieve_and_generate(query, user_role)
    return ChatResponse(
        answer=response_data["answer"],
        sources=response_data["sources"]
    )

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
