"""
Authentication dependencies for role-based access control.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import jwt

from app.core.config import get_settings
from app.core.roles import UserRole
from app.services.supabase import SupabaseService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current authenticated user from JWT token."""
    try:
        config = get_settings()
        
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            config.secret_key,
            algorithms=[config.algorithm]
        )
        
        user_id = payload.get("user_id")
        user_type = payload.get("user_type")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        return {
            "user_id": user_id,
            "user_type": user_type,
            "email": email,
            "payload": payload
        }
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require admin role for access."""
    if current_user.get("user_type") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_teacher_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require teacher or admin role for access."""
    user_type = current_user.get("user_type")
    if user_type not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or admin access required"
        )
    return current_user


async def get_student_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require student role for access (students can only access their own data)."""
    if current_user.get("user_type") != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user


class RoleChecker:
    """Class-based role checker for more flexible role requirements."""
    
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)):
        user_type = current_user.get("user_type")
        if user_type not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in self.allowed_roles]}"
            )
        return current_user


# Convenience instances
require_admin = RoleChecker([UserRole.ADMIN])
require_teacher_or_admin = RoleChecker([UserRole.TEACHER, UserRole.ADMIN])
require_any_role = RoleChecker([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
