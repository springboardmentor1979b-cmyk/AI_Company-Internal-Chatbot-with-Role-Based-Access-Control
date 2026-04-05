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
from src.auth.auth_handler import (
    authenticate, create_token, decode_token, create_user,
    log_query, get_dashboard_metrics, get_user_history
)
from src.rag.pipeline import answer_query

app = FastAPI(
    title="Nexus Intel API",
    description="Cyberpunk RAG backend with RBAC and telemetry",
    version="2.0.0",
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


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") not in ["c_level", "admin"]:
        raise HTTPException(status_code=403, detail="Administrator/C-Level access required.")
    return user


# ── Routes ────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "nexus-intel-api"}


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="INVALID CREDENTIALS")
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
    
    # ── LOG TELEMETRY FOR DASHBOARD ──
    log_query(current_user["username"], role, req.question)
    
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

@app.get("/chat/history")
def history(current_user: dict = Depends(get_current_user)):
    """Fetch the query history for the currently authenticated user."""
    history_records = get_user_history(current_user["username"])
    return {"history": history_records}

@app.get("/admin/dashboard")
def dashboard(current_user: dict = Depends(get_current_user)):
    """Fetch total aggregated metrics for the Analytics UI. Automatically filters by user role."""
    return get_dashboard_metrics(role_filter=current_user.get("role", "employees"))


@app.post("/admin/create-user", status_code=201)
def admin_create_user(
    req: CreateUserRequest,
    _admin: dict = Depends(require_admin),
):
    ok = create_user(req.username, req.password, req.role, req.department)
    if not ok:
        raise HTTPException(status_code=409, detail=f"USER {req.username} ALREADY EXISTS")
    return {"message": f"USER {req.username} ALLOCATED: {req.role}"}


# ── Run directly ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
