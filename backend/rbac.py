from fastapi import Depends, HTTPException, status
from backend.auth import get_current_user
from backend.models import User

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get the authenticated user and optionally check if active."""
    return current_user

def get_user_role(current_user: User = Depends(get_current_active_user)) -> str:
    """Extract user role from the authenticated user to enforce RBAC."""
    return current_user.role

class RoleChecker:
    """Dependency class to check if a user has a specific role to access an endpoint."""
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles and user.role != "C-Level":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions"
            )
        return user
