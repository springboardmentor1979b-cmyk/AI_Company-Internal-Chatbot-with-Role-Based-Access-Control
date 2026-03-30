from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import timedelta
from contextlib import asynccontextmanager

from backend.database import engine, Base, get_db
from backend.models import User
from backend.auth import verify_password, get_password_hash, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.rag_pipeline import query_rag

# Initialize DB
Base.metadata.create_all(bind=engine)

def create_initial_users():
    db = next(get_db())
    try:
        if db.query(User).count() == 0:
            users = [
                {"username": "finance_user", "password": "pass123", "role": "Finance"},
                {"username": "hr_user", "password": "pass123", "role": "HR"},
                {"username": "eng_user", "password": "pass123", "role": "Engineering"},
                {"username": "marketing_user", "password": "pass123", "role": "Marketing"},
                {"username": "employee_user", "password": "pass123", "role": "Employee"},
                {"username": "c_level_user", "password": "pass123", "role": "C-Level"}
            ]
            for u in users:
                db_user = User(
                    username=u["username"],
                    password_hash=get_password_hash(u["password"]),
                    role=u["role"]
                )
                db.add(db_user)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_initial_users()
    yield

app = FastAPI(title="Company Internal Chatbot API", lifespan=lifespan)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    role: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest, current_user: User = Depends(get_current_user)):
    user_role = current_user.role
    
    try:
        # Pass the query and user_role for RBAC filtering in the vector db
        response = query_rag(request.query, user_role)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
