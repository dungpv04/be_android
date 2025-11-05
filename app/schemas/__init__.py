"""Schemas module initialization."""

from .auth import (
    LoginRequest, LoginResponse, RegisterRequest, TokenData,
    BaseResponse, ErrorResponse, PaginationParams, PaginatedResponse,
    AdminProfile, TeacherProfile, StudentProfile, UserMeResponse
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
from .admin import (
    AdminCreate, AdminUpdate, AdminResponse
)
from .classes import (
    ClassCreate, ClassUpdate, ClassResponse,
    TeachingSessionCreate, TeachingSessionUpdate, TeachingSessionResponse,
    AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceDetailResponse,
    ClassStudentCreate, ClassStudentResponse, ClassStudentDetailResponse,
    StudentClassDetailResponse, MultipleSessionsAttendanceRequest
)
from .excel import (
    TeacherExcelRow, StudentExcelRow, BulkImportResult, ExcelValidationError
)

__all__ = [
    # Auth schemas
    "LoginRequest", "LoginResponse", "RegisterRequest", "TokenData",
    "BaseResponse", "ErrorResponse", "PaginationParams", "PaginatedResponse",
    "AdminProfile", "TeacherProfile", "StudentProfile", "UserMeResponse",
    
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
    
    # Admin schemas
    "AdminCreate", "AdminUpdate", "AdminResponse",
    
    # Class schemas
    "ClassCreate", "ClassUpdate", "ClassResponse",
    "TeachingSessionCreate", "TeachingSessionUpdate", "TeachingSessionResponse",
    "AttendanceCreate", "AttendanceUpdate", "AttendanceResponse", "AttendanceDetailResponse",
    "ClassStudentCreate", "ClassStudentResponse", "ClassStudentDetailResponse",
    "StudentClassDetailResponse", "MultipleSessionsAttendanceRequest",
    
    # Excel schemas
    "TeacherExcelRow", "StudentExcelRow", "BulkImportResult", "ExcelValidationError"
]
