"""
Class and teaching session schemas.
"""
from typing import Optional, List
from datetime import date, time
from pydantic import Field, validator
from enum import Enum

from app.schemas.base import (
    BaseSchema, 
    CreateSchemaBase, 
    UpdateSchemaBase, 
    ResponseSchemaBase, 
    TimestampSchema
)
from app.schemas.academic import Subject
from app.schemas.users import Teacher, Student


class ClassStatus(str, Enum):
    """Class status enumeration."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Class schemas
class ClassBase(BaseSchema):
    """Base class schema."""
    
    class_code: str = Field(..., min_length=1, max_length=50, description="Unique class code")
    class_name: str = Field(..., min_length=1, max_length=255, description="Class name")
    description: Optional[str] = Field(None, max_length=1000, description="Class description")
    subject_id: int = Field(..., description="Subject ID")
    teacher_id: int = Field(..., description="Teacher ID")
    status: ClassStatus = Field(default=ClassStatus.ACTIVE, description="Class status")
    start_date: Optional[date] = Field(None, description="Class start date")
    end_date: Optional[date] = Field(None, description="Class end date")
    max_students: Optional[int] = Field(None, ge=1, le=1000, description="Maximum students allowed")
    
    @validator('class_code')
    def validate_class_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Class code must be alphanumeric (with optional - or _)')
        return v.upper()
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v <= start_date:
            raise ValueError('End date must be after start date')
        return v


class ClassCreate(ClassBase, CreateSchemaBase):
    """Schema for creating a class."""
    pass


class ClassUpdate(UpdateSchemaBase):
    """Schema for updating a class."""
    
    class_code: Optional[str] = Field(None, min_length=1, max_length=50)
    class_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    status: Optional[ClassStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_students: Optional[int] = Field(None, ge=1, le=1000)
    
    @validator('class_code')
    def validate_class_code(cls, v):
        if v is not None and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Class code must be alphanumeric (with optional - or _)')
        return v.upper() if v else None
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v <= start_date:
            raise ValueError('End date must be after start date')
        return v


class Class(ClassBase, ResponseSchemaBase, TimestampSchema):
    """Class response schema."""
    
    subject: Optional[Subject] = None
    teacher: Optional[Teacher] = None
    current_students: Optional[int] = Field(None, description="Current student count")
    sessions_count: Optional[int] = Field(None, description="Number of teaching sessions")


# ClassStudent schemas (enrollment)
class ClassStudentBase(BaseSchema):
    """Base class student enrollment schema."""
    
    class_id: int = Field(..., description="Class ID")
    student_id: int = Field(..., description="Student ID")
    enrollment_date: Optional[date] = Field(None, description="Enrollment date")
    is_active: bool = Field(default=True, description="Enrollment status")
    notes: Optional[str] = Field(None, max_length=500, description="Enrollment notes")


class ClassStudentCreate(ClassStudentBase, CreateSchemaBase):
    """Schema for creating class student enrollment."""
    pass


class ClassStudentUpdate(UpdateSchemaBase):
    """Schema for updating class student enrollment."""
    
    enrollment_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class ClassStudent(ClassStudentBase, ResponseSchemaBase, TimestampSchema):
    """Class student enrollment response schema."""
    
    class_info: Optional[Class] = None
    student: Optional[Student] = None
    attendance_rate: Optional[float] = Field(None, description="Student attendance percentage")


class SessionType(str, Enum):
    """Teaching session type enumeration."""
    
    LECTURE = "lecture"
    PRACTICE = "practice"
    LAB = "lab"
    EXAM = "exam"
    REVIEW = "review"
    OTHER = "other"


# TeachingSession schemas
class TeachingSessionBase(BaseSchema):
    """Base teaching session schema."""
    
    class_id: int = Field(..., description="Class ID")
    session_name: str = Field(..., min_length=1, max_length=255, description="Session name")
    session_type: SessionType = Field(default=SessionType.LECTURE, description="Session type")
    session_date: date = Field(..., description="Session date")
    start_time: time = Field(..., description="Session start time")
    end_time: time = Field(..., description="Session end time")
    location: Optional[str] = Field(None, max_length=255, description="Session location")
    description: Optional[str] = Field(None, max_length=1000, description="Session description")
    is_mandatory: bool = Field(default=True, description="Whether attendance is mandatory")
    qr_code: Optional[str] = Field(None, description="QR code for attendance")
    qr_expires_at: Optional[date] = Field(None, description="QR code expiration")
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        start_time = values.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('session_date')
    def validate_session_date(cls, v):
        from datetime import date
        if v < date.today():
            raise ValueError('Session date cannot be in the past')
        return v


class TeachingSessionCreate(TeachingSessionBase, CreateSchemaBase):
    """Schema for creating a teaching session."""
    
    generate_qr: bool = Field(default=True, description="Whether to generate QR code")


class TeachingSessionUpdate(UpdateSchemaBase):
    """Schema for updating a teaching session."""
    
    session_name: Optional[str] = Field(None, min_length=1, max_length=255)
    session_type: Optional[SessionType] = None
    session_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_mandatory: Optional[bool] = None
    qr_code: Optional[str] = None
    qr_expires_at: Optional[date] = None
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        start_time = values.get('start_time')
        if start_time and v and v <= start_time:
            raise ValueError('End time must be after start time')
        return v


class TeachingSession(TeachingSessionBase, ResponseSchemaBase, TimestampSchema):
    """Teaching session response schema."""
    
    class_info: Optional[Class] = None
    attendance_count: Optional[int] = Field(None, description="Number of students attended")
    total_students: Optional[int] = Field(None, description="Total students in class")
    attendance_rate: Optional[float] = Field(None, description="Attendance percentage")


# QR Code specific schemas
class QRCodeGenerate(BaseSchema):
    """Schema for generating QR code."""
    
    session_id: int = Field(..., description="Teaching session ID")
    expires_in_minutes: int = Field(default=30, ge=5, le=480, description="QR code validity in minutes")


class QRCodeResponse(BaseSchema):
    """QR code response schema."""
    
    qr_code: str = Field(..., description="Generated QR code")
    expires_at: date = Field(..., description="QR code expiration time")
    session_id: int = Field(..., description="Teaching session ID")


class QRCodeValidate(BaseSchema):
    """Schema for validating QR code attendance."""
    
    qr_code: str = Field(..., description="QR code to validate")
    student_id: Optional[int] = Field(None, description="Student ID (optional if from auth)")


# Class statistics schemas
class ClassStatistics(BaseSchema):
    """Class statistics schema."""
    
    class_id: int
    total_sessions: int
    completed_sessions: int
    upcoming_sessions: int
    total_students: int
    average_attendance_rate: float
    most_attended_session: Optional[dict] = None
    least_attended_session: Optional[dict] = None


class StudentClassStatistics(BaseSchema):
    """Student statistics for a specific class."""
    
    student_id: int
    class_id: int
    total_sessions: int
    attended_sessions: int
    attendance_rate: float
    late_attendances: int
    early_departures: int
    last_attendance: Optional[date] = None
