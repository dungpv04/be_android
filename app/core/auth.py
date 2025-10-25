from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from supabase import Client
from app.core.config import settings
from app.core.database import get_supabase_admin


class AuthService:
    """Authentication service for handling JWT tokens and user authentication."""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    async def authenticate_user_with_supabase(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Supabase Auth."""
        try:
            supabase = get_supabase_admin()
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {
                    "user": response.user,
                    "session": response.session
                }
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    async def create_user_with_supabase(self, email: str, password: str, user_metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create user with Supabase Auth using service role."""
        try:
            supabase = get_supabase_admin()
            
            # Use the auth.admin API with service role key
            response = supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "user_metadata": user_metadata or {},
                "email_confirm": True  # Auto-confirm email in development
            })
            
            if response.user:
                return {
                    "user": response.user,
                    "session": None  # Admin created users don't have sessions
                }
            return None
        except Exception as e:
            print(f"Create user error: {e}")
            # Fallback: try regular sign up if admin creation fails
            try:
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": user_metadata or {}
                    }
                })
                
                if response.user:
                    return {
                        "user": response.user,
                        "session": response.session
                    }
            except Exception as fallback_error:
                print(f"Fallback sign up error: {fallback_error}")
            
            return None
    
    async def get_current_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get current user from JWT token."""
        try:
            supabase = get_supabase_admin()
            response = supabase.auth.get_user(token)
            return response.user if response.user else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None


# Global instance
auth_service = AuthService()
