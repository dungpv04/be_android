"""
User models: students and teachers.
"""
from sqlalchemy import Column, String, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel


class Teacher(BaseModel):
    """Teacher model."""
    
    __tablename__ = "teachers"
    
    teacher_code = Column(String, nullable=False, unique=True, comment="Unique teacher code")
    full_name = Column(String, nullable=False, comment="Teacher full name")
    phone = Column(String, nullable=True, comment="Phone number")
    birth_date = Column(Date, nullable=True, comment="Date of birth")
    auth_id = Column(UUID(as_uuid=True), nullable=False, comment="Supabase auth user ID")
    
    # Relationships
    classes = relationship("Class", back_populates="teacher", lazy="select")
    
    def __repr__(self):
        return f"<Teacher(code='{self.teacher_code}', name='{self.full_name}')>"


class Student(BaseModel):
    """Student model."""
    
    __tablename__ = "students"
    
    student_code = Column(String, nullable=False, unique=True, comment="Unique student code")
    full_name = Column(String, nullable=False, comment="Student full name")
    phone = Column(String, nullable=True, comment="Phone number")
    birth_date = Column(Date, nullable=True, comment="Date of birth")
    auth_id = Column(UUID(as_uuid=True), nullable=False, comment="Supabase auth user ID")
    
    # Foreign keys
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=True)
    cohort_id = Column(Integer, ForeignKey("cohorts.id"), nullable=True)
    class_id = Column(Integer, nullable=True, comment="Direct class reference")
    
    # Relationships
    major = relationship("Major", back_populates="students", lazy="select")
    cohort = relationship("Cohort", back_populates="students", lazy="select")
    class_students = relationship("ClassStudent", back_populates="student", lazy="select")
    attendances = relationship("Attendance", back_populates="student", lazy="select")
    face_templates = relationship("FaceTemplate", back_populates="student", lazy="select")
    
    def __repr__(self):
        return f"<Student(code='{self.student_code}', name='{self.full_name}')>"
    
    @property
    def enrolled_classes(self):
        """Get all classes this student is enrolled in."""
        return [cs.class_ for cs in self.class_students if cs.status == 'active']
