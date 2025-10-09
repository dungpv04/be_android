"""
User schemas: students and teachers.
"""
from typing import Optional
from datetime import date
from pydantic import Field, EmailStr, validator
import uuid

from app.schemas.base import (
    BaseSchema, 
    CreateSchemaBase, 
    UpdateSchemaBase, 
    ResponseSchemaBase, 
    TimestampSchema
)
from app.schemas.academic import Major, Cohort


# Teacher schemas
class TeacherBase(BaseSchema):
    """Base teacher schema."""
    
    teacher_code: str = Field(..., min_length=1, max_length=50, description="Unique teacher code")
    full_name: str = Field(..., min_length=1, max_length=255, description="Teacher full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    
    @validator('teacher_code')
    def validate_teacher_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Teacher code must be alphanumeric (with optional - or _)')
        return v.upper()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            # Simple phone validation - adjust based on your requirements
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v is not None:
            from datetime import date
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18 or age > 100:
                raise ValueError('Age must be between 18 and 100 years')
        return v


class TeacherCreate(TeacherBase, CreateSchemaBase):
    """Schema for creating a teacher."""
    
    auth_id: uuid.UUID = Field(..., description="Supabase auth user ID")


class TeacherUpdate(UpdateSchemaBase):
    """Schema for updating a teacher."""
    
    teacher_code: Optional[str] = Field(None, min_length=1, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    
    @validator('teacher_code')
    def validate_teacher_code(cls, v):
        if v is not None and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Teacher code must be alphanumeric (with optional - or _)')
        return v.upper() if v else None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v is not None:
            from datetime import date
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18 or age > 100:
                raise ValueError('Age must be between 18 and 100 years')
        return v


class Teacher(TeacherBase, ResponseSchemaBase, TimestampSchema):
    """Teacher response schema."""
    
    auth_id: uuid.UUID
    classes_count: Optional[int] = Field(None, description="Number of classes taught")


# Student schemas
class StudentBase(BaseSchema):
    """Base student schema."""
    
    student_code: str = Field(..., min_length=1, max_length=50, description="Unique student code")
    full_name: str = Field(..., min_length=1, max_length=255, description="Student full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    major_id: Optional[int] = Field(None, description="Major ID")
    cohort_id: Optional[int] = Field(None, description="Cohort ID")
    class_id: Optional[int] = Field(None, description="Direct class reference")
    
    @validator('student_code')
    def validate_student_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Student code must be alphanumeric (with optional - or _)')
        return v.upper()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v is not None:
            from datetime import date
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 14 or age > 80:
                raise ValueError('Age must be between 14 and 80 years')
        return v


class StudentCreate(StudentBase, CreateSchemaBase):
    """Schema for creating a student."""
    
    auth_id: uuid.UUID = Field(..., description="Supabase auth user ID")


class StudentUpdate(UpdateSchemaBase):
    """Schema for updating a student."""
    
    student_code: Optional[str] = Field(None, min_length=1, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    class_id: Optional[int] = None
    
    @validator('student_code')
    def validate_student_code(cls, v):
        if v is not None and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Student code must be alphanumeric (with optional - or _)')
        return v.upper() if v else None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v is not None:
            from datetime import date
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 14 or age > 80:
                raise ValueError('Age must be between 14 and 80 years')
        return v


class Student(StudentBase, ResponseSchemaBase, TimestampSchema):
    """Student response schema."""
    
    auth_id: uuid.UUID
    major: Optional[Major] = None
    cohort: Optional[Cohort] = None
    enrollment_count: Optional[int] = Field(None, description="Number of enrolled classes")


# Authentication schemas
class UserLogin(BaseSchema):
    """User login schema."""
    
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="User password")


class UserRegister(BaseSchema):
    """User registration schema."""
    
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, max_length=128, description="User password")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    user_type: str = Field(..., description="User type: 'student' or 'teacher'")
    
    # Additional fields based on user type
    student_code: Optional[str] = Field(None, description="Required for students")
    teacher_code: Optional[str] = Field(None, description="Required for teachers")
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    major_id: Optional[int] = Field(None, description="Required for students")
    cohort_id: Optional[int] = Field(None, description="Required for students")
    
    @validator('user_type')
    def validate_user_type(cls, v):
        if v not in ['student', 'teacher']:
            raise ValueError('User type must be either "student" or "teacher"')
        return v
    
    @validator('student_code')
    def validate_student_code(cls, v, values):
        user_type = values.get('user_type')
        if user_type == 'student' and not v:
            raise ValueError('Student code is required for student registration')
        return v
    
    @validator('teacher_code')
    def validate_teacher_code(cls, v, values):
        user_type = values.get('user_type')
        if user_type == 'teacher' and not v:
            raise ValueError('Teacher code is required for teacher registration')
        return v


class Token(BaseSchema):
    """JWT token response schema."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: str = Field(..., description="User ID")
    user_type: str = Field(..., description="User type")
    expires_in: Optional[int] = Field(None, description="Token expiry in seconds")


class TokenData(BaseSchema):
    """Token payload data."""
    
    user_id: str
    user_type: str
    payload: Optional[dict] = None
