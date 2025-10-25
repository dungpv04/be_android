"""Repositories module initialization."""

from .base import BaseRepository
from .academic import (
    FacultyRepository, DepartmentRepository, MajorRepository,
    SubjectRepository, AcademicYearRepository, CohortRepository,
    SemesterRepository, StudyPhaseRepository
)
from .users import StudentRepository, TeacherRepository
from .classes import (
    ClassRepository, TeachingSessionRepository, AttendanceRepository,
    ClassStudentRepository
)

__all__ = [
    "BaseRepository",
    "FacultyRepository", "DepartmentRepository", "MajorRepository",
    "SubjectRepository", "AcademicYearRepository", "CohortRepository",
    "StudentRepository", "TeacherRepository",
    "ClassRepository", "TeachingSessionRepository", "AttendanceRepository",
    "ClassStudentRepository"
]
