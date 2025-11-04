from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: str = "Operation successful"
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    message: str
    error_code: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[dict]
    total: int
    page: int
    limit: int
    total_pages: int


# Authentication Schemas
class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    password: str
    full_name: str
    user_type: str  # student, teacher, admin


class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[str] = None


# Profile Schemas for /me endpoint
class AdminProfile(BaseModel):
    """Admin profile schema."""
    id: int
    auth_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TeacherProfile(BaseModel):
    """Teacher profile schema."""
    id: int
    faculty_id: Optional[int] = None
    department_id: Optional[int] = None
    teacher_code: str
    full_name: str
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    hometown: Optional[str] = None
    auth_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class StudentProfile(BaseModel):
    """Student profile schema."""
    id: int
    faculty_id: Optional[int] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    class_name: str
    student_code: str
    full_name: str
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    hometown: Optional[str] = None
    auth_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserMeResponse(BaseModel):
    """User profile response for /me endpoint."""
    id: str  # auth_id
    auth_id: str
    email: str
    user_type: str  # admin, teacher, student, unknown
    profile: Optional[dict] = None  # AdminProfile, TeacherProfile, or StudentProfile
