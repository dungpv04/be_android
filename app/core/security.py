"""
Security and authentication utilities.
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

from app.core.config import get_auth_config


class SecurityManager:
    """Handles security operations like password hashing and JWT tokens."""
    
    def __init__(self):
        self.auth_config = get_auth_config()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security_scheme = HTTPBearer()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.auth_config.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            self.auth_config.secret_key, 
            algorithm=self.auth_config.algorithm
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token, 
                self.auth_config.secret_key, 
                algorithms=[self.auth_config.algorithm]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_current_user_from_token(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> Dict[str, Any]:
        """Extract user information from JWT token."""
        token = credentials.credentials
        payload = self.verify_token(token)
        
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user_id,
            "user_type": user_type,
            "payload": payload
        }


class TokenData:
    """Token data structure."""
    
    def __init__(self, user_id: str, user_type: str, payload: Optional[Dict] = None):
        self.user_id = user_id
        self.user_type = user_type
        self.payload = payload or {}


class RoleChecker:
    """Role-based access control checker."""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: Dict = Depends(SecurityManager().get_current_user_from_token)):
        user_type = current_user.get("user_type")
        
        if user_type not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        
        return TokenData(
            user_id=current_user["user_id"],
            user_type=user_type,
            payload=current_user["payload"]
        )


# Global security manager instance
security_manager = SecurityManager()

# Role checkers
require_teacher = RoleChecker(["teacher"])
require_student = RoleChecker(["student"])
require_any_user = RoleChecker(["teacher", "student"])

# Convenience functions
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> TokenData:
    """Get current user from JWT token."""
    user_data = security_manager.get_current_user_from_token(credentials)
    return TokenData(
        user_id=user_data["user_id"],
        user_type=user_data["user_type"],
        payload=user_data["payload"]
    )

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token."""
    return security_manager.create_access_token(data, expires_delta)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return security_manager.verify_password(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return security_manager.get_password_hash(password)
