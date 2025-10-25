from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from supabase import Client
from app.core.database import get_supabase
from app.core.auth import auth_service
from app.schemas import LoginRequest, LoginResponse, RegisterRequest, BaseResponse
from app.services import StudentService, TeacherService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    supabase: Client = Depends(get_supabase)
):
    """User login endpoint."""
    try:
        # Authenticate with Supabase
        auth_result = await auth_service.authenticate_user_with_supabase(
            login_data.email, login_data.password
        )
        
        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = auth_result["user"]
        session = auth_result["session"]
        
        # Get user details based on user type
        user_details = None
        user_type = user.user_metadata.get("user_type", "student")
        
        if user_type == "student":
            student_service = StudentService(supabase)
            student = await student_service.get_by_auth_id(user.id)
            if student:
                user_details = {
                    "id": student.id,
                    "student_code": student.student_code,
                    "full_name": student.full_name,
                    "user_type": "student"
                }
        elif user_type == "teacher":
            teacher_service = TeacherService(supabase)
            teacher = await teacher_service.get_by_auth_id(user.id)
            if teacher:
                user_details = {
                    "id": teacher.id,
                    "teacher_code": teacher.teacher_code,
                    "full_name": teacher.full_name,
                    "user_type": "teacher"
                }
        
        return LoginResponse(
            access_token=session.access_token,
            user=user_details or {"id": user.id, "email": user.email, "user_type": user_type}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/register", response_model=BaseResponse)
async def register(
    register_data: RegisterRequest,
    supabase: Client = Depends(get_supabase)
):
    """User registration endpoint."""
    try:
        user_type = register_data.user_type.lower()
        
        if user_type == "student":
            student_service = StudentService(supabase)
            # For simplicity, we'll generate a student code
            import time
            student_code = f"STU{int(time.time())}"
            
            from app.schemas import StudentCreate
            student_data = StudentCreate(
                student_code=student_code,
                full_name=register_data.full_name,
                email=register_data.email,
                password=register_data.password
            )
            
            student = await student_service.create_student_with_auth(student_data)
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create student account"
                )
            
            return BaseResponse(message="Student account created successfully")
            
        elif user_type == "teacher":
            teacher_service = TeacherService(supabase)
            # For simplicity, we'll generate a teacher code
            import time
            teacher_code = f"TEA{int(time.time())}"
            
            from app.schemas import TeacherCreate
            teacher_data = TeacherCreate(
                teacher_code=teacher_code,
                full_name=register_data.full_name,
                email=register_data.email,
                password=register_data.password
            )
            
            teacher = await teacher_service.create_teacher_with_auth(teacher_data)
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create teacher account"
                )
            
            return BaseResponse(message="Teacher account created successfully")
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user type. Must be 'student' or 'teacher'"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """Get current user information."""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user_from_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Get user details based on user type
        user_type = user.user_metadata.get("user_type", "student")
        user_details = {"id": user.id, "email": user.email, "user_type": user_type}
        
        if user_type == "student":
            student_service = StudentService(supabase)
            student = await student_service.get_by_auth_id(user.id)
            if student:
                user_details.update({
                    "profile_id": student.id,
                    "student_code": student.student_code,
                    "full_name": student.full_name
                })
        elif user_type == "teacher":
            teacher_service = TeacherService(supabase)
            teacher = await teacher_service.get_by_auth_id(user.id)
            if teacher:
                user_details.update({
                    "profile_id": teacher.id,
                    "teacher_code": teacher.teacher_code,
                    "full_name": teacher.full_name
                })
        
        return BaseResponse(data=user_details)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )
