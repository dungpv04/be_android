"""
Repositories package.
"""

from app.repositories.base import BaseRepository
from app.repositories.users import StudentRepository, TeacherRepository
from app.repositories.subjects import SubjectRepository

__all__ = ["BaseRepository", "StudentRepository", "TeacherRepository", "SubjectRepository"]
