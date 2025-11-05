from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel, Field


# Academic Year Schemas
class AcademicYearCreate(BaseModel):
    """Schema for creating academic year."""
    name: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date


class AcademicYearUpdate(BaseModel):
    """Schema for updating academic year."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AcademicYearResponse(BaseModel):
    """Schema for academic year response."""
    id: int
    name: str
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime


# Faculty Schemas
class FacultyCreate(BaseModel):
    """Schema for creating faculty."""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)


class FacultyUpdate(BaseModel):
    """Schema for updating faculty."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)


class FacultyResponse(BaseModel):
    """Schema for faculty response."""
    id: int
    name: str
    code: str
    created_at: datetime
    updated_at: datetime


# Department Schemas
class DepartmentCreate(BaseModel):
    """Schema for creating department."""
    faculty_id: int
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)


class DepartmentUpdate(BaseModel):
    """Schema for updating department."""
    faculty_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)


class DepartmentResponse(BaseModel):
    """Schema for department response."""
    id: int
    faculty_id: Optional[int]
    name: str
    code: str
    created_at: datetime
    updated_at: datetime


# Major Schemas
class MajorCreate(BaseModel):
    """Schema for creating major."""
    faculty_id: int
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)


class MajorUpdate(BaseModel):
    """Schema for updating major."""
    faculty_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)


class MajorResponse(BaseModel):
    """Schema for major response."""
    id: int
    faculty_id: Optional[int]
    name: str
    code: str
    created_at: datetime
    updated_at: datetime


# Cohort Schemas
class CohortCreate(BaseModel):
    """Schema for creating cohort."""
    name: str = Field(..., min_length=1, max_length=255)
    start_year: int = Field(..., ge=2000, le=2100)
    end_year: int = Field(..., ge=2000, le=2100)


class CohortUpdate(BaseModel):
    """Schema for updating cohort."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_year: Optional[int] = Field(None, ge=2000, le=2100)
    end_year: Optional[int] = Field(None, ge=2000, le=2100)


class CohortResponse(BaseModel):
    """Schema for cohort response."""
    id: int
    name: str
    start_year: int
    end_year: int
    created_at: datetime
    updated_at: datetime


# Subject Schemas
class SubjectCreate(BaseModel):
    """Schema for creating subject."""
    department_id: int
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    credits: int = Field(..., ge=1, le=10)


class SubjectUpdate(BaseModel):
    """Schema for updating subject."""
    department_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    credits: Optional[int] = Field(None, ge=1, le=10)


class SubjectResponse(BaseModel):
    """Schema for subject response."""
    id: int
    department_id: Optional[int]
    name: str
    code: str
    credits: Optional[int]
    created_at: datetime
    updated_at: datetime


# Semester Schemas
class SemesterCreate(BaseModel):
    """Schema for creating semester."""
    academic_year_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date


class SemesterUpdate(BaseModel):
    """Schema for updating semester."""
    academic_year_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class SemesterResponse(BaseModel):
    """Schema for semester response."""
    id: int
    academic_year_id: Optional[int]
    name: str
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime


# Study Phase Schemas
class StudyPhaseCreate(BaseModel):
    """Schema for creating study phase."""
    semester_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date


class StudyPhaseUpdate(BaseModel):
    """Schema for updating study phase."""
    semester_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class StudyPhaseResponse(BaseModel):
    """Schema for study phase response."""
    id: int
    semester_id: Optional[int]
    name: str
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime
