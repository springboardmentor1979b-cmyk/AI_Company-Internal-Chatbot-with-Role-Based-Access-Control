"""
main.py — FastAPI backend
─────────────────────────
Endpoints:
  POST /auth/login          → JWT token
  POST /chat/query          → RAG answer (protected)
  GET  /auth/me             → current user info (protected)
  POST /admin/create-user   → create user (admin only)
  GET  /health              → liveness check
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import jwt

from backend.models import (
    LoginRequest, TokenResponse,
    QueryRequest, QueryResponse,
    CreateUserRequest,
)
from src.auth.auth_handler import authenticate, create_token, decode_token, create_user
from src.rag.pipeline import answer_query

app = FastAPI(
    title="Infobot",
    description="RAG-powered chatbot with Role-Based Access Control",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# ── Auth helpers ──────────────────────────────────────────────

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def require_c_level(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "c_level":
        raise HTTPException(status_code=403, detail="C-Level access required.")
    return user


# ── Routes ────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "company-chatbot"}


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_token(user)
    return TokenResponse(
        access_token=token,
        username=user["username"],
        role=user["role"],
        department=user.get("department", ""),
    )


@app.get("/auth/me")
def me(current_user: dict = Depends(get_current_user)):
    return {k: v for k, v in current_user.items() if k != "exp"}


@app.post("/chat/query", response_model=QueryResponse)
def query(req: QueryRequest, current_user: dict = Depends(get_current_user)):
    role = current_user.get("role", "employees")
    result = answer_query(
        question=req.question,
        user_role=role,
        top_k=req.top_k,
    )
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        chunks_used=result["chunks_used"],
        role=result["role"],
    )


@app.post("/admin/create-user", status_code=201)
def admin_create_user(
    req: CreateUserRequest,
    _admin: dict = Depends(require_c_level),
):
    ok = create_user(req.username, req.password, req.role, req.department)
    if not ok:
        raise HTTPException(status_code=409, detail=f"User '{req.username}' already exists.")
    return {"message": f"User '{req.username}' created with role '{req.role}'."}


# ── Run directly ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
