"""
Repositories package.
"""

from app.repositories.base import BaseRepository
from app.repositories.users import StudentRepository, TeacherRepository

__all__ = ["BaseRepository", "StudentRepository", "TeacherRepository"]
