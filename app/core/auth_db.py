"""
JWT-based authentication dependencies for role checking.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from app.core.security import SecurityManager

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current user from JWT token.
    """
    try:
        security_manager = SecurityManager()
        
        # Decode and verify JWT token
        payload = security_manager.verify_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return payload
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )


async def get_admin_user_db(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Admin role authentication dependency.
    """
    if current_user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def get_teacher_user_db(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Teacher role authentication dependency.
    """
    if current_user.get("user_role") != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    
    return current_user


async def get_student_user_db(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Student role authentication dependency.
    """
    if current_user.get("user_role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    
    return current_user


async def get_teacher_or_admin_user_db(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Teacher or admin role authentication dependency.
    """
    if current_user.get("user_role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or admin access required"
        )
    
    return current_user
