from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseModelConfig(BaseModel):
    """Base model with common configuration."""
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class AcademicYear(BaseModelConfig):
    """Academic Year model."""
    id: Optional[int] = None
    name: str
    start_date: date
    end_date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Faculty(BaseModelConfig):
    """Faculty model."""
    id: Optional[int] = None
    name: str
    code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Department(BaseModelConfig):
    """Department model."""
    id: Optional[int] = None
    faculty_id: Optional[int] = None
    name: str
    code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Major(BaseModelConfig):
    """Major model."""
    id: Optional[int] = None
    faculty_id: Optional[int] = None
    name: str
    code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Cohort(BaseModelConfig):
    """Cohort model."""
    id: Optional[int] = None
    name: str
    start_year: int
    end_year: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Subject(BaseModelConfig):
    """Subject model."""
    id: Optional[int] = None
    department_id: Optional[int] = None
    name: str
    code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Semester(BaseModelConfig):
    """Semester model."""
    id: Optional[int] = None
    academic_year_id: Optional[int] = None
    name: str
    start_date: date
    end_date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StudyPhase(BaseModelConfig):
    """Study Phase model."""
    id: Optional[int] = None
    semester_id: Optional[int] = None
    name: str
    start_date: date
    end_date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Teacher(BaseModelConfig):
    """Teacher model."""
    id: Optional[int] = None
    faculty_id: Optional[int] = None
    department_id: Optional[int] = None
    teacher_code: str
    full_name: str
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    hometown: Optional[str] = None
    auth_id: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Student(BaseModelConfig):
    """Student model."""
    id: Optional[int] = None
    faculty_id: Optional[int] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    class_name: str
    student_code: str
    full_name: str
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    hometown: Optional[str] = None
    auth_id: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Admin(BaseModelConfig):
    """Admin model."""
    id: Optional[int] = None
    auth_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Class(BaseModelConfig):
    """Class model."""
    id: Optional[int] = None
    name: str
    code: str
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    faculty_id: Optional[int] = None
    department_id: Optional[int] = None
    major_id: Optional[int] = None
    cohort_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    semester_id: Optional[int] = None
    study_phase_id: Optional[int] = None
    status: Optional[str] = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ClassStudent(BaseModelConfig):
    """Class Student relationship model."""
    id: Optional[int] = None
    class_id: Optional[int] = None
    student_id: Optional[int] = None
    enrolled_at: Optional[datetime] = None
    status: Optional[str] = "active"


class TeachingSession(BaseModelConfig):
    """Teaching Session model."""
    id: Optional[int] = None
    class_id: Optional[int] = None
    session_date: date
    start_time: time
    end_time: time
    session_type: Optional[str] = None
    qr_code: Optional[str] = None
    qr_expired_at: Optional[datetime] = None
    status: Optional[str] = "Open"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Attendance(BaseModelConfig):
    """Attendance model."""
    id: Optional[int] = None
    session_id: Optional[int] = None
    student_id: Optional[int] = None
    attendance_time: Optional[datetime] = None
    status: Optional[str] = None
    confidence_score: Optional[float] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FaceTemplate(BaseModelConfig):
    """Face Template model."""
    id: Optional[int] = None
    student_id: Optional[int] = None
    image_path: str
    face_encoding: Optional[str] = None
    is_primary: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Admin(BaseModelConfig):
    """Admin model."""
    id: Optional[int] = None
    auth_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
