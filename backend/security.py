import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User

_DEFAULT_KEY = "dragon-rbac-supersecret-2030"
SECRET_KEY   = os.environ.get("SECRET_KEY", _DEFAULT_KEY)
ALGORITHM    = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

if SECRET_KEY == _DEFAULT_KEY:
    print("⚠️  WARNING: Using default SECRET_KEY — set SECRET_KEY env variable in production!")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise exc
    except JWTError:
        raise exc

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise exc
    # Respect is_active flag if column exists
    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")
    return user
