"""
Schemas package initialization.
Provides convenient imports for all schema classes.
"""

# Base schemas
from app.schemas.base import (
    BaseSchema,
    CreateSchemaBase,
    UpdateSchemaBase,
    ResponseSchemaBase,
    TimestampSchema,
    PaginationParams,
    PaginatedResponse
)

# Academic schemas
from app.schemas.academic import (
    # Major schemas
    MajorBase, MajorCreate, MajorUpdate, Major,
    # Subject schemas
    SubjectBase, SubjectCreate, SubjectUpdate, Subject,
    # Cohort schemas
    CohortBase, CohortCreate, CohortUpdate, Cohort
)

# User schemas
from app.schemas.users import (
    # Teacher schemas
    TeacherBase, TeacherCreate, TeacherUpdate, Teacher,
    # Student schemas
    StudentBase, StudentCreate, StudentUpdate, Student,
    # Authentication schemas
    UserLogin, UserRegister, Token, TokenData
)

# Class schemas
from app.schemas.classes import (
    # Class schemas
    ClassBase, ClassCreate, ClassUpdate, Class, ClassStatus,
    # Class enrollment schemas
    ClassStudentBase, ClassStudentCreate, ClassStudentUpdate, ClassStudent,
    # Teaching session schemas
    TeachingSessionBase, TeachingSessionCreate, TeachingSessionUpdate, 
    TeachingSession, SessionType,
    # QR Code schemas
    QRCodeGenerate, QRCodeResponse, QRCodeValidate,
    # Statistics schemas
    ClassStatistics, StudentClassStatistics
)

# Attendance schemas
from app.schemas.attendance import (
    # Attendance schemas
    AttendanceBase, AttendanceCreate, AttendanceUpdate, Attendance,
    AttendanceStatus, AttendanceMethod,
    # Bulk operations
    BulkAttendanceCreate, BulkAttendanceResponse,
    # QR attendance
    QRAttendanceCreate,
    # Face recognition schemas
    FaceTemplateBase, FaceTemplateCreate, FaceTemplateUpdate, FaceTemplate,
    FaceRecognitionRequest, FaceRecognitionResponse,
    # Reports and analytics
    AttendanceReportFilter, AttendanceReportSummary,
    StudentAttendanceReport, ClassAttendanceReport,
    # Notifications
    AttendanceNotification, AttendanceReminder
)

__all__ = [
    # Base schemas
    "BaseSchema", "CreateSchemaBase", "UpdateSchemaBase", 
    "ResponseSchemaBase", "TimestampSchema", "PaginationParams", "PaginatedResponse",
    
    # Academic schemas
    "MajorBase", "MajorCreate", "MajorUpdate", "Major",
    "SubjectBase", "SubjectCreate", "SubjectUpdate", "Subject",
    "CohortBase", "CohortCreate", "CohortUpdate", "Cohort",
    
    # User schemas
    "TeacherBase", "TeacherCreate", "TeacherUpdate", "Teacher",
    "StudentBase", "StudentCreate", "StudentUpdate", "Student",
    "UserLogin", "UserRegister", "Token", "TokenData",
    
    # Class schemas
    "ClassBase", "ClassCreate", "ClassUpdate", "Class", "ClassStatus",
    "ClassStudentBase", "ClassStudentCreate", "ClassStudentUpdate", "ClassStudent",
    "TeachingSessionBase", "TeachingSessionCreate", "TeachingSessionUpdate", 
    "TeachingSession", "SessionType",
    "QRCodeGenerate", "QRCodeResponse", "QRCodeValidate",
    "ClassStatistics", "StudentClassStatistics",
    
    # Attendance schemas
    "AttendanceBase", "AttendanceCreate", "AttendanceUpdate", "Attendance",
    "AttendanceStatus", "AttendanceMethod",
    "BulkAttendanceCreate", "BulkAttendanceResponse",
    "QRAttendanceCreate",
    "FaceTemplateBase", "FaceTemplateCreate", "FaceTemplateUpdate", "FaceTemplate",
    "FaceRecognitionRequest", "FaceRecognitionResponse",
    "AttendanceReportFilter", "AttendanceReportSummary",
    "StudentAttendanceReport", "ClassAttendanceReport",
    "AttendanceNotification", "AttendanceReminder"
]
