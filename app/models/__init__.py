"""
Database models for the attendance management system.
"""
from app.models.base import BaseModel, TimestampMixin
from app.models.academic import Major, Subject, Cohort
from app.models.users import Teacher, Student
from app.models.classes import Class, ClassStudent, TeachingSession
from app.models.attendance import Attendance, FaceTemplate

# Export all models
__all__ = [
    "BaseModel",
    "TimestampMixin",
    "Major",
    "Subject", 
    "Cohort",
    "Teacher",
    "Student",
    "Class",
    "ClassStudent",
    "TeachingSession",
    "Attendance",
    "FaceTemplate",
]
