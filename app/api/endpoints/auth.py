"""
Authentication API endpoints for Supabase.
"""
from fastapi import APIRouter, HTTPException, status, Header
from fastapi.security import HTTPBearer
from typing import Dict, Any, Optional

from app.core.security import SecurityManager
from app.services.supabase import SupabaseService
from app.repositories.teachers import TeacherRepository
from app.repositories.students import StudentRepository
from app.repositories.admin import AdminRepository
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
        
        auth_id = auth_response['id']
        user_email = auth_response.get('email', '')
        
        # Look up user profile and role from database tables
        user_role = None
        user_profile_id = None
        user_profile = None
        
        # Check admin table first
        admin_repo = AdminRepository()
        admin_profile = await admin_repo.get_by_auth_id(auth_id)
        if admin_profile:
            user_role = "admin"
            user_profile_id = admin_profile["id"]
            user_profile = admin_profile
        
        # Check teacher table if not admin
        if not user_role:
            teacher_repo = TeacherRepository()
            teacher_profile = await teacher_repo.get_by_auth_id(auth_id)
            if teacher_profile:
                user_role = "teacher"
                user_profile_id = teacher_profile["id"]
                user_profile = teacher_profile
        
        # Check student table if not admin or teacher
        if not user_role:
            student_repo = StudentRepository()
            student_profile = await student_repo.get_by_auth_id(auth_id)
            if student_profile:
                user_role = "student"
                user_profile_id = student_profile["id"]
                user_profile = student_profile
        
        # If no profile found in any table, deny access
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User profile not found. Contact administrator."
            )
        
        # Generate JWT token with user profile info
        access_token = security_manager.create_access_token(
            data={
                "auth_id": auth_id,
                "user_role": user_role,
                "user_profile_id": user_profile_id,
                "email": user_email
            }
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=auth_id,
            user_type=user_role
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
async def get_current_user_info(
    authorization: str = Header(..., description="Bearer token")
):
    """Get current user information based on JWT token."""
    try:
        # Extract token from Bearer header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        token = authorization.split(" ")[1]
        
        # Decode JWT token
        security_manager = SecurityManager()
        payload = security_manager.verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_type = payload.get("user_role")
        auth_id = payload.get("auth_id")
        user_profile_id = payload.get("user_profile_id")
        
        if not user_type or not auth_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user information based on user_type
        user_info = None
        
        if user_type == "admin":
            admin_repo = AdminRepository()
            user_info = await admin_repo.get_by_auth_id(auth_id)
            if user_info:
                user_info["user_type"] = "admin"
                
        elif user_type == "teacher":
            teacher_repo = TeacherRepository()
            user_info = await teacher_repo.get_by_auth_id(auth_id)
            if user_info:
                user_info["user_type"] = "teacher"
                
        elif user_type == "student":
            student_repo = StudentRepository()
            user_info = await student_repo.get_by_auth_id(auth_id)
            if user_info:
                user_info["user_type"] = "student"
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Add auth information to response
        user_info["auth_id"] = auth_id
        user_info["email"] = payload.get("email")
        
        return {
            "message": "User information retrieved successfully",
            "user": user_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user information: {str(e)}"
        )
