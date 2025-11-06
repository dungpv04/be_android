from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# Student Schemas
class StudentCreate(BaseModel):
    """Schema for creating student."""
    faculty_id: Optional[int] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    class_name: str = Field(..., min_length=1, max_length=255)
    student_code: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    hometown: Optional[str] = Field(None, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)


class StudentUpdate(BaseModel):
    """Schema for updating student."""
    faculty_id: Optional[int] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    class_name: Optional[str] = Field(None, min_length=1, max_length=255)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    hometown: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class StudentResponse(BaseModel):
    """Schema for student response."""
    id: int
    faculty_id: Optional[int]
    major_id: Optional[int]
    cohort_id: Optional[int]
    class_name: str
    student_code: str
    full_name: str
    phone: Optional[str]
    birth_date: Optional[date]
    hometown: Optional[str]
    auth_id: str
    email: Optional[str]
    created_at: datetime
    updated_at: datetime


# Teacher Schemas
class TeacherCreate(BaseModel):
    """Schema for creating teacher."""
    faculty_id: Optional[int] = None
    department_id: Optional[int] = None
    teacher_code: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    hometown: Optional[str] = Field(None, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)


class TeacherUpdate(BaseModel):
    """Schema for updating teacher."""
    faculty_id: Optional[int] = None
    department_id: Optional[int] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    hometown: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class TeacherResponse(BaseModel):
    """Schema for teacher response."""
    id: int
    faculty_id: Optional[int]
    department_id: Optional[int]
    teacher_code: str
    full_name: str
    phone: Optional[str]
    birth_date: Optional[date]
    hometown: Optional[str]
    auth_id: str
    email: Optional[str]
    created_at: datetime
    updated_at: datetime
