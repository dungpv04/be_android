from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from supabase import Client
from app.core.database import get_supabase
from app.core.auth import auth_service
from app.schemas import LoginRequest, LoginResponse, RegisterRequest, BaseResponse, UserMeResponse
from app.services import StudentService, TeacherService, AdminService

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
        
        # Get user details - check all user types to determine the correct one
        user_details = None
        
        # Check if user is admin first
        admin_service = AdminService(supabase)
        admin = await admin_service.get_by_auth_id(user.id)
        if admin:
            user_details = {
                "id": admin.id,
                "email": user.email,
                "user_type": "admin"
            }
        else:
            # Check if user is teacher
            teacher_service = TeacherService(supabase)
            teacher = await teacher_service.get_by_auth_id(user.id)
            if teacher:
                user_details = {
                    "id": teacher.id,
                    "teacher_code": teacher.teacher_code,
                    "full_name": teacher.full_name,
                    "user_type": "teacher"
                }
            else:
                # Check if user is student
                student_service = StudentService(supabase)
                student = await student_service.get_by_auth_id(user.id)
                if student:
                    user_details = {
                        "id": student.id,
                        "student_code": student.student_code,
                        "full_name": student.full_name,
                        "user_type": "student"
                    }
        
        return LoginResponse(
            access_token=session.access_token,
            user=user_details or {"id": user.id, "email": user.email, "user_type": "unknown"}
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


@router.get("/me", response_model=BaseResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """Get current user information with full profile data."""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user_from_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Get user details - check all user types to determine the correct one and return full profile
        user_details = None
        
        # Check if user is admin first
        admin_service = AdminService(supabase)
        admin = await admin_service.get_by_auth_id(user.id)
        if admin:
            user_details = {
                "id": admin.id,
                "auth_id": admin.auth_id,
                "email": user.email,
                "user_type": "admin",
                "profile": {
                    "id": admin.id,
                    "auth_id": admin.auth_id,
                    "created_at": admin.created_at.isoformat() if admin.created_at else None,
                    "updated_at": admin.updated_at.isoformat() if admin.updated_at else None
                }
            }
        else:
            # Check if user is teacher
            teacher_service = TeacherService(supabase)
            teacher = await teacher_service.get_by_auth_id(user.id)
            if teacher:
                user_details = {
                    "id": teacher.id,
                    "auth_id": teacher.auth_id,
                    "email": user.email,
                    "user_type": "teacher",
                    "profile": {
                        "id": teacher.id,
                        "faculty_id": teacher.faculty_id,
                        "department_id": teacher.department_id,
                        "teacher_code": teacher.teacher_code,
                        "full_name": teacher.full_name,
                        "phone": teacher.phone,
                        "birth_date": teacher.birth_date.isoformat() if teacher.birth_date else None,
                        "hometown": teacher.hometown,
                        "auth_id": teacher.auth_id,
                        "created_at": teacher.created_at.isoformat() if teacher.created_at else None,
                        "updated_at": teacher.updated_at.isoformat() if teacher.updated_at else None
                    }
                }
            else:
                # Check if user is student
                student_service = StudentService(supabase)
                student = await student_service.get_by_auth_id(user.id)
                if student:
                    user_details = {
                        "id": student.id,
                        "auth_id": student.auth_id,
                        "email": user.email,
                        "user_type": "student",
                        "profile": {
                            "id": student.id,
                            "faculty_id": student.faculty_id,
                            "major_id": student.major_id,
                            "cohort_id": student.cohort_id,
                            "class_name": student.class_name,
                            "student_code": student.student_code,
                            "full_name": student.full_name,
                            "phone": student.phone,
                            "birth_date": student.birth_date.isoformat() if student.birth_date else None,
                            "hometown": student.hometown,
                            "auth_id": student.auth_id,
                            "created_at": student.created_at.isoformat() if student.created_at else None,
                            "updated_at": student.updated_at.isoformat() if student.updated_at else None
                        }
                    }
        
        if not user_details:
            # Fallback for unknown user type
            user_details = {
                "id": user.id,
                "email": user.email,
                "user_type": "unknown",
                "auth_id": user.id,
                "profile": None
            }
        
        return BaseResponse(
            message="User profile retrieved successfully",
            data=user_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )
