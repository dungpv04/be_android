"""Schemas module initialization."""

from .auth import (
    LoginRequest, LoginResponse, RegisterRequest, TokenData,
    BaseResponse, ErrorResponse, PaginationParams, PaginatedResponse
)
from .academic import (
    AcademicYearCreate, AcademicYearUpdate, AcademicYearResponse,
    FacultyCreate, FacultyUpdate, FacultyResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    MajorCreate, MajorUpdate, MajorResponse,
    CohortCreate, CohortUpdate, CohortResponse,
    SubjectCreate, SubjectUpdate, SubjectResponse,
    SemesterCreate, SemesterUpdate, SemesterResponse,
    StudyPhaseCreate, StudyPhaseUpdate, StudyPhaseResponse
)
from .users import (
    StudentCreate, StudentUpdate, StudentResponse,
    TeacherCreate, TeacherUpdate, TeacherResponse
)
from .classes import (
    ClassCreate, ClassUpdate, ClassResponse,
    TeachingSessionCreate, TeachingSessionUpdate, TeachingSessionResponse,
    AttendanceCreate, AttendanceUpdate, AttendanceResponse,
    ClassStudentCreate, ClassStudentResponse
)

__all__ = [
    # Auth schemas
    "LoginRequest", "LoginResponse", "RegisterRequest", "TokenData",
    "BaseResponse", "ErrorResponse", "PaginationParams", "PaginatedResponse",
    
    # Academic schemas
    "AcademicYearCreate", "AcademicYearUpdate", "AcademicYearResponse",
    "FacultyCreate", "FacultyUpdate", "FacultyResponse",
    "DepartmentCreate", "DepartmentUpdate", "DepartmentResponse",
    "MajorCreate", "MajorUpdate", "MajorResponse",
    "CohortCreate", "CohortUpdate", "CohortResponse",
    "SubjectCreate", "SubjectUpdate", "SubjectResponse",
    "SemesterCreate", "SemesterUpdate", "SemesterResponse",
    "StudyPhaseCreate", "StudyPhaseUpdate", "StudyPhaseResponse",
    
    # User schemas
    "StudentCreate", "StudentUpdate", "StudentResponse",
    "TeacherCreate", "TeacherUpdate", "TeacherResponse",
    
    # Class schemas
    "ClassCreate", "ClassUpdate", "ClassResponse",
    "TeachingSessionCreate", "TeachingSessionUpdate", "TeachingSessionResponse",
    "AttendanceCreate", "AttendanceUpdate", "AttendanceResponse",
    "ClassStudentCreate", "ClassStudentResponse"
]
