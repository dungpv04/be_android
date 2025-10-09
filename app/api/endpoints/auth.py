"""
Authentication API endpoints for Supabase.
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any

from app.core.security import SecurityManager
from app.services.supabase import SupabaseService
from app.schemas.users import UserLogin, Token

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """User login with Supabase authentication."""
    try:
        # Initialize services
        supabase_service = SupabaseService()
        security_manager = SecurityManager()
        
        # Authenticate with Supabase
        auth_response = await supabase_service.authenticate_user(
            user_credentials.email, 
            user_credentials.password
        )
        
        if not auth_response or not auth_response.get('id'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user_id = auth_response['id']
        user_email = auth_response.get('email', '')
        user_metadata = auth_response.get('user_metadata', {})
        
        # Determine user type from metadata or email
        user_type = user_metadata.get('role', 'student')  # Get from metadata first
        
        # Fallback to email-based detection if no role in metadata
        if not user_type or user_type == 'student':
            if "admin" in user_email.lower():
                user_type = "admin"
            elif "teacher" in user_email.lower():
                user_type = "teacher"
            else:
                user_type = "student"
        
        # Generate JWT token
        access_token = security_manager.create_access_token(
            data={"user_id": user_id, "user_type": user_type, "email": user_email}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            user_type=user_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/register")
async def register(user_data: Dict[str, Any]):
    """User registration with Supabase."""
    try:
        supabase_service = SupabaseService()
        
        email = user_data.get("email")
        password = user_data.get("password")
        user_type = user_data.get("user_type", "student")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Register user with Supabase
        result = await supabase_service.register_user(
            email=email,
            password=password,
            user_metadata={
                "user_type": user_type,
                "full_name": user_data.get("full_name", ""),
            }
        )
        
        return {
            "message": "User registered successfully",
            "user_id": result["id"],
            "email": result["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """User logout (for completeness)."""
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user():
    """Get current user info (placeholder)."""
    return {"message": "User info endpoint - requires authentication"}
