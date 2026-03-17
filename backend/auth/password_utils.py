from typing import Dict
from fastapi import HTTPException, status
from backend.schemas import UserRole


# ----------------------------------------
# Mock User Database (Replace with DB later)
# ----------------------------------------
# NOTE:
# - Passwords are plain text for demo.
# - In production, always hash passwords.
# ----------------------------------------

mock_users_db: Dict[str, Dict] = {
    "finance_user": {
        "password": "finance123",
        "role": UserRole.Finance
    },
    "hr_user": {
        "password": "hr123456",
        "role": UserRole.HR
    },
    "engineering_user": {
        "password": "eng123",
        "role": UserRole.Engineering
    },
    "marketing_user": {
        "password": "market123",
        "role": UserRole.Marketing
    },
    "admin": {
        "password": "adminsecure",
        "role": UserRole.CLevel
    }
}


# ----------------------------------------
# Authentication Function
# ----------------------------------------

def authenticate_user(username: str, password: str) -> UserRole:
    """
    Validates user credentials and returns user role.
    Raises HTTPException if credentials are invalid.
    """

    user = mock_users_db.get(username)

    if not user or user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return user["role"]
