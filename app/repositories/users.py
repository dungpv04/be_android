"""
User repositories: students and teachers.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.repositories.base import BaseRepository
from app.models.users import Student, Teacher
from app.schemas.users import (
    StudentCreate, StudentUpdate, 
    TeacherCreate, TeacherUpdate
)


class StudentRepository(BaseRepository[Student, StudentCreate, StudentUpdate]):
    """Repository for student operations."""
    
    def __init__(self):
        super().__init__(Student)
    
    def get_by_student_code(self, db: Session, student_code: str) -> Optional[Student]:
        """Get student by student code."""
        return db.query(Student).filter(Student.student_code == student_code.upper()).first()
    
    def get_by_auth_id(self, db: Session, auth_id: str) -> Optional[Student]:
        """Get student by auth ID."""
        return db.query(Student).filter(Student.auth_id == auth_id).first()
    
    def get_by_major(self, db: Session, major_id: int, skip: int = 0, limit: int = 100) -> List[Student]:
        """Get students by major."""
        return db.query(Student).filter(Student.major_id == major_id).offset(skip).limit(limit).all()
    
    def get_by_cohort(self, db: Session, cohort_id: int, skip: int = 0, limit: int = 100) -> List[Student]:
        """Get students by cohort."""
        return db.query(Student).filter(Student.cohort_id == cohort_id).offset(skip).limit(limit).all()
    
    def get_by_class(self, db: Session, class_id: int, skip: int = 0, limit: int = 100) -> List[Student]:
        """Get students by class."""
        return db.query(Student).filter(Student.class_id == class_id).offset(skip).limit(limit).all()
    
    def search_students(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Student]:
        """Search students by name or code."""
        search_filter = or_(
            Student.full_name.ilike(f"%{query}%"),
            Student.student_code.ilike(f"%{query}%")
        )
        return db.query(Student).filter(search_filter).offset(skip).limit(limit).all()


class TeacherRepository(BaseRepository[Teacher, TeacherCreate, TeacherUpdate]):
    """Repository for teacher operations."""
    
    def __init__(self):
        super().__init__(Teacher)
    
    def get_by_teacher_code(self, db: Session, teacher_code: str) -> Optional[Teacher]:
        """Get teacher by teacher code."""
        return db.query(Teacher).filter(Teacher.teacher_code == teacher_code.upper()).first()
    
    def get_by_auth_id(self, db: Session, auth_id: str) -> Optional[Teacher]:
        """Get teacher by auth ID."""
        return db.query(Teacher).filter(Teacher.auth_id == auth_id).first()
    
    def search_teachers(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Teacher]:
        """Search teachers by name or code."""
        search_filter = or_(
            Teacher.full_name.ilike(f"%{query}%"),
            Teacher.teacher_code.ilike(f"%{query}%")
        )
        return db.query(Teacher).filter(search_filter).offset(skip).limit(limit).all()
    
    def get_active_teachers(self, db: Session, skip: int = 0, limit: int = 100) -> List[Teacher]:
        """Get all active teachers."""
        return db.query(Teacher).offset(skip).limit(limit).all()
