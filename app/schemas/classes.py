from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# Class Schemas
class ClassCreate(BaseModel):
    """Schema for creating class."""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    faculty_id: Optional[int] = None
    department_id: Optional[int] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    semester_id: Optional[int] = None
    study_phase_id: Optional[int] = None


class ClassUpdate(BaseModel):
    """Schema for updating class."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    faculty_id: Optional[int] = None
    department_id: Optional[int] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    semester_id: Optional[int] = None
    study_phase_id: Optional[int] = None
    status: Optional[str] = None


class ClassResponse(BaseModel):
    """Schema for class response."""
    id: int
    name: str
    code: str
    subject_id: Optional[int]
    teacher_id: Optional[int]
    faculty_id: Optional[int]
    department_id: Optional[int]
    major_id: Optional[int]
    cohort_id: Optional[int]
    academic_year_id: Optional[int]
    semester_id: Optional[int]
    study_phase_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime


# Teaching Session Schemas
class TeachingSessionCreate(BaseModel):
    """Schema for creating teaching session."""
    class_id: int
    session_date: date
    start_time: time
    end_time: time
    session_type: Optional[str] = Field(None, max_length=50)


class TeachingSessionUpdate(BaseModel):
    """Schema for updating teaching session."""
    session_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    session_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = None


class TeachingSessionResponse(BaseModel):
    """Schema for teaching session response."""
    id: int
    class_id: int
    session_date: date
    start_time: time
    end_time: time
    session_type: Optional[str]
    qr_code: Optional[str]
    qr_expired_at: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime


# Attendance Schemas
class AttendanceCreate(BaseModel):
    """Schema for creating attendance."""
    session_id: int
    student_id: int
    status: str = Field(..., pattern="^(present|absent|late)$")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['present', 'absent', 'late']:
            raise ValueError('Status must be present, absent, or late')
        return v


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance."""
    status: Optional[str] = Field(None, pattern="^(present|absent|late)$")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ['present', 'absent', 'late']:
            raise ValueError('Status must be present, absent, or late')
        return v


class AttendanceResponse(BaseModel):
    """Schema for attendance response."""
    id: int
    session_id: int
    student_id: int
    attendance_time: Optional[datetime]
    status: str
    confidence_score: Optional[float]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    updated_at: datetime


class AttendanceDetailResponse(BaseModel):
    """Schema for detailed attendance response with joined data."""
    # Attendance details
    id: int
    session_id: int
    student_id: int
    attendance_time: Optional[datetime]
    status: str
    confidence_score: Optional[float]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    updated_at: datetime
    # Student details
    student_name: str
    student_code: str
    student_phone: Optional[str] = None
    student_hometown: Optional[str] = None
    student_class_name: Optional[str] = None
    # Session details
    session_date: date
    session_start_time: time
    session_end_time: time
    session_type: Optional[str] = None
    session_status: str
    # Class details
    class_id: int
    class_name: str
    class_code: str
    # Subject details
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    # Teacher details
    teacher_name: Optional[str] = None
    teacher_code: Optional[str] = None


# Class Student Schemas
class ClassStudentCreate(BaseModel):
    """Schema for enrolling student in class."""
    student_id: int


class ClassStudentResponse(BaseModel):
    """Schema for class student response."""
    id: int
    class_id: int
    student_id: int
    enrolled_at: datetime
    status: str


class ClassStudentDetailResponse(BaseModel):
    """Schema for detailed class student response with student info."""
    id: int
    class_id: int
    student_id: int
    enrolled_at: datetime
    status: str
    # Student details
    student_name: str
    student_code: str
    student_email: Optional[str] = None
    student_phone: Optional[str] = None
    student_hometown: Optional[str] = None
    class_name: Optional[str] = None


class StudentClassDetailResponse(BaseModel):
    """Schema for detailed class response for a student with enrollment info."""
    # Class details
    id: int
    name: str
    code: str
    subject_id: int
    teacher_id: int
    faculty_id: int
    department_id: int
    major_id: int
    cohort_id: int
    academic_year_id: int
    semester_id: int
    study_phase_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    # Joined details
    faculty_name: Optional[str] = None
    department_name: Optional[str] = None
    major_name: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    teacher_name: Optional[str] = None
    teacher_code: Optional[str] = None
    cohort_name: Optional[str] = None
    academic_year_name: Optional[str] = None
    semester_name: Optional[str] = None
    study_phase_name: Optional[str] = None
    student_count: int
    # Enrollment details
    enrollment_id: int
    enrolled_at: datetime
    enrollment_status: str
