"""
Admin schemas for user management operations.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field, EmailStr, validator
import uuid

from app.schemas.base import (
    BaseSchema, 
    CreateSchemaBase, 
    UpdateSchemaBase, 
    ResponseSchemaBase, 
    TimestampSchema
)
from app.core.roles import UserRole


# Admin schemas
class AdminBase(BaseSchema):
    """Base admin schema."""
    
    auth_id: uuid.UUID = Field(..., description="Supabase auth user ID")


class AdminCreate(AdminBase, CreateSchemaBase):
    """Schema for creating an admin."""
    pass


class AdminUpdate(UpdateSchemaBase):
    """Schema for updating an admin."""
    
    auth_id: Optional[uuid.UUID] = None


class Admin(AdminBase, ResponseSchemaBase, TimestampSchema):
    """Admin response schema."""
    pass


# Teacher creation schema
class TeacherCreateRequest(BaseSchema):
    """Schema for creating a new teacher with account."""
    
    email: EmailStr = Field(..., description="Teacher email")
    password: str = Field(..., min_length=6, max_length=128, description="Password")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    teacher_code: str = Field(..., min_length=1, max_length=50, description="Unique teacher code")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    birth_date: Optional[datetime] = Field(None, description="Date of birth")
    
    @validator('teacher_code')
    def validate_teacher_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Teacher code must be alphanumeric (with optional - or _)')
        return v.upper()


# Student creation schema
class StudentCreateRequest(BaseSchema):
    """Schema for creating a new student with account."""
    
    email: EmailStr = Field(..., description="Student email")
    password: str = Field(..., min_length=6, max_length=128, description="Password")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    student_code: str = Field(..., min_length=1, max_length=50, description="Unique student code")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    birth_date: Optional[datetime] = Field(None, description="Date of birth")
    major_id: Optional[int] = Field(None, description="Major ID")
    cohort_id: Optional[int] = Field(None, description="Cohort ID")
    class_id: Optional[int] = Field(None, description="Direct class assignment")
    
    @validator('student_code')
    def validate_student_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Student code must be alphanumeric (with optional - or _)')
        return v.upper()


# Response schemas
class TeacherCreateResponse(BaseSchema):
    """Response for teacher creation."""
    
    message: str
    auth_id: uuid.UUID
    email: str
    teacher_code: str
    full_name: str
    created_at: datetime


class StudentCreateResponse(BaseSchema):
    """Response for student creation."""
    
    message: str
    auth_id: uuid.UUID
    email: str
    student_code: str
    full_name: str
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    class_id: Optional[int] = None
    created_at: datetime


class UserUpdateRequest(BaseSchema):
    """Schema for updating a user."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[datetime] = None
    
    # Teacher specific
    teacher_code: Optional[str] = None
    
    # Student specific
    student_code: Optional[str] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None


class UserResponse(BaseSchema):
    """User response schema."""
    
    auth_id: uuid.UUID
    email: str
    role: UserRole
    full_name: str
    phone: Optional[str] = None
    birth_date: Optional[datetime] = None
    created_at: datetime
    
    # Role specific data
    teacher_code: Optional[str] = None
    student_code: Optional[str] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None


class UserListResponse(BaseSchema):
    """Response for user listing."""
    
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class UserDeleteResponse(BaseSchema):
    """Response for user deletion."""
    
    message: str
    deleted_auth_id: uuid.UUID
    deleted_role: UserRole


# Role management schemas
class RoleAssignRequest(BaseSchema):
    """Schema for assigning roles to users."""
    
    auth_id: uuid.UUID = Field(..., description="User auth ID")
    new_role: UserRole = Field(..., description="New role to assign")


class BulkUserOperation(BaseSchema):
    """Schema for bulk user operations."""
    
    user_ids: List[uuid.UUID] = Field(..., description="List of user auth IDs")
    operation: str = Field(..., description="Operation: 'activate', 'deactivate', 'delete'")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['activate', 'deactivate', 'delete']
        if v not in allowed_operations:
            raise ValueError(f'Operation must be one of: {allowed_operations}')
        return v


class BulkOperationResponse(BaseSchema):
    """Response for bulk operations."""
    
    operation: str
    total_requested: int
    successful: int
    failed: int
    errors: List[str] = []
    successful_ids: List[uuid.UUID] = []
