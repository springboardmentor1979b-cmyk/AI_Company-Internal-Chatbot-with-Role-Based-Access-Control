from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .database import SessionLocal
from .models import User
from .security import create_access_token, get_current_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router      = APIRouter()

# ── ROLE KEYS — stored server-side only, never sent to frontend ──────────────
_ROLE_KEYS = {
    "Finance":     "FIN-2030",
    "HR":          "HR-2030",
    "Marketing":   "MKT-2030",
    "Engineering": "ENG-2030",
    "Employee":    "EMP-2030",
    "C-Level":     "ADMIN-2030",
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# ── VERIFY ROLE KEY (step-2 MFA) — server-side validation ────────────────────
@router.post("/verify-role-key")
def verify_role_key(
    role_key: str,
    user=Depends(get_current_user)
):
    """
    Validates the departmental role passkey server-side.
    The key is never sent to the frontend; the frontend only submits the user's input.
    """
    expected = _ROLE_KEYS.get(user.role, "")
    if not expected or role_key.strip() != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid access key for role '{user.role}'."
        )
    return {"verified": True, "role": user.role}


# ── REGISTER — C-Level auth required ─────────────────────────────────────────
@router.post("/register")
def register(
    username: str,
    password: str,
    role: str,
    current_user=Depends(get_current_user),   # ← now requires authentication
    db: Session = Depends(get_db)
):
    """Register a new user — requires a valid C-Level JWT token."""
    if current_user.role != "C-Level":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only C-Level administrators can register new users."
        )
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=username,
        password=hash_password(password),
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User '{username}' registered as {role}"}
