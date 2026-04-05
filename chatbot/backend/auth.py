"""
auth.py — JWT authentication
POST /auth/login   → access_token + refresh_token
POST /auth/refresh → new access_token
POST /auth/logout  → revoke session
GET  /auth/me      → current user info + stats
"""

import hashlib
import uuid
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

import db

# ─── Config ──────────────────────────────────────────────────────────────────
# Load from environment variables or use defaults
SECRET_KEY     = os.getenv("JWT_SECRET_KEY", "nexusai-super-secret-jwt-key-change-in-production")
ALGORITHM      = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_EXPIRE  = timedelta(hours=int(os.getenv("JWT_ACCESS_EXPIRE_HOURS", "8")))
REFRESH_EXPIRE = timedelta(days=int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7")))

bearer = HTTPBearer()
router = APIRouter()

# ─── Schemas ──────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email:    str
    password: str

class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    user:          dict

class RegisterRequest(BaseModel):
    email:    EmailStr
    name:     str
    password: str
    role:     str  # e.g., "finance", "marketing", etc.

class RefreshRequest(BaseModel):
    refresh_token: str

# ─── JWT helpers ─────────────────────────────────────────────────────────────
def _make_token(user_id: int, role: str, kind: str, expire: timedelta) -> tuple[str, str]:
    """Returns (token, jti)"""
    jti = str(uuid.uuid4())
    exp = datetime.utcnow() + expire
    payload = {
        "sub":  str(user_id),
        "role": role,
        "kind": kind,   # "access" | "refresh"
        "jti":  jti,
        "exp":  exp,
        "iat":  datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, exp.isoformat()

def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ─── Dependency ───────────────────────────────────────────────────────────────
def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    payload = _decode_token(creds.credentials)
    if payload.get("kind") != "access":
        raise HTTPException(status_code=401, detail="Not an access token")
    if not db.is_session_valid(payload["jti"]):
        raise HTTPException(status_code=401, detail="Session revoked or expired")
    user = db.get_user_by_id(int(payload["sub"]))
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ─── Routes ───────────────────────────────────────────────────────────────────
@router.post("/register")
def register(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if req.role not in ["finance", "marketing", "hr", "engineering", "employees", "c_level"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    department = {
        "finance": "Finance",
        "marketing": "Marketing",
        "hr": "HR",
        "engineering": "Engineering",
        "employees": "General",
        "c_level": "Executive"
    }.get(req.role, "General")
    
    avatar_initials = "".join(word[0] for word in req.name.split() if word).upper()[:2]
    
    user_id = db.create_user(req.email, req.name, req.password, req.role, department, avatar_initials)
    if not user_id:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return {"message": "User registered successfully", "user_id": user_id}

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = db.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    hashed = hashlib.sha256(req.password.encode()).hexdigest()
    if hashed != user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access,  jti_a, exp_a = _make_token(user["id"], user["role"], "access",  ACCESS_EXPIRE)
    refresh, jti_r, exp_r = _make_token(user["id"], user["role"], "refresh", REFRESH_EXPIRE)

    db.create_session(user["id"], jti_a, exp_a)
    db.create_session(user["id"], jti_r, exp_r)
    db.update_last_login(user["id"])

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user={
            "id":         user["id"],
            "name":       user["name"],
            "email":      user["email"],
            "role":       user["role"],
            "department": user["department"],
            "avatar_initials": user["avatar_initials"],
            "last_login": user["last_login"],
        },
    )

@router.post("/refresh")
def refresh_token(req: RefreshRequest):
    payload = _decode_token(req.refresh_token)
    if payload.get("kind") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")
    if not db.is_session_valid(payload["jti"]):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    user = db.get_user_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Revoke old refresh, issue new pair
    db.revoke_session(payload["jti"])
    access,  jti_a, exp_a = _make_token(user["id"], user["role"], "access",  ACCESS_EXPIRE)
    refresh, jti_r, exp_r = _make_token(user["id"], user["role"], "refresh", REFRESH_EXPIRE)
    db.create_session(user["id"], jti_a, exp_a)
    db.create_session(user["id"], jti_r, exp_r)

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/logout")
def logout(
    req: Optional[RefreshRequest] = None,
    creds: HTTPAuthorizationCredentials = Depends(bearer),
):
    payload = _decode_token(creds.credentials)
    db.revoke_session(payload["jti"])
    if req and req.refresh_token:
        try:
            rp = _decode_token(req.refresh_token)
            db.revoke_session(rp["jti"])
        except Exception:
            pass
    return {"detail": "Logged out"}

@router.get("/me")
def me(user=Depends(get_current_user)):
    stats = db.get_user_stats(user["id"])
    return {
        "user":  {k: user[k] for k in ["id","name","email","role","department","avatar_initials","last_login"]},
        "stats": stats,
    }