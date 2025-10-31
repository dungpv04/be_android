"""Services module initialization."""

from .base import BaseService
from .academic import (
    FacultyService, DepartmentService, MajorService,
    SubjectService, AcademicYearService, CohortService,
    SemesterService, StudyPhaseService
)
from .users import StudentService, TeacherService
from .admin import AdminService
from .classes import (
    ClassService, TeachingSessionService, AttendanceService,
    ClassStudentService
)

__all__ = [
    "BaseService",
    "FacultyService", "DepartmentService", "MajorService",
    "SubjectService", "AcademicYearService", "CohortService",
    "SemesterService", "StudyPhaseService",
    "StudentService", "TeacherService", "AdminService",
    "ClassService", "TeachingSessionService", "AttendanceService",
    "ClassStudentService"
]
