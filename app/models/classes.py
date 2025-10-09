"""
Class and teaching session models.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Date, Time, Text, DateTime, CheckConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Class(BaseModel):
    """Class model linking teachers and subjects."""
    
    __tablename__ = "classes"
    
    name = Column(String, nullable=False, comment="Class name")
    code = Column(String, nullable=False, unique=True, comment="Unique class code")
    status = Column(String, default="active", comment="Class status")
    
    # Foreign keys
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive')", name="classes_status_check"),
    )
    
    # Relationships
    subject = relationship("Subject", back_populates="classes", lazy="select")
    teacher = relationship("Teacher", back_populates="classes", lazy="select")
    class_students = relationship("ClassStudent", back_populates="class_", lazy="select")
    teaching_sessions = relationship("TeachingSession", back_populates="class_", lazy="select")
    
    def __repr__(self):
        return f"<Class(code='{self.code}', name='{self.name}')>"
    
    @property
    def enrolled_students(self):
        """Get all active students in this class."""
        return [cs.student for cs in self.class_students if cs.status == 'active']
    
    @property
    def active_sessions(self):
        """Get all active teaching sessions."""
        return [session for session in self.teaching_sessions if session.status == 'Open']


class ClassStudent(BaseModel):
    """Many-to-many relationship between classes and students."""
    
    __tablename__ = "class_students"
    
    status = Column(String, default="active", comment="Enrollment status")
    
    # Foreign keys
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'dropped')", name="class_students_status_check"),
    )
    
    # Relationships
    class_ = relationship("Class", back_populates="class_students", lazy="select")
    student = relationship("Student", back_populates="class_students", lazy="select")
    
    def __repr__(self):
        return f"<ClassStudent(class_id={self.class_id}, student_id={self.student_id}, status='{self.status}')>"


class TeachingSession(BaseModel):
    """Teaching session model for scheduled classes."""
    
    __tablename__ = "teaching_sessions"
    
    session_date = Column(Date, nullable=False, comment="Session date")
    start_time = Column(Time, nullable=False, comment="Session start time")
    end_time = Column(Time, nullable=False, comment="Session end time")
    session_type = Column(String, nullable=False, comment="Type of session")
    qr_code = Column(Text, nullable=True, comment="QR code for attendance")
    qr_expired_at = Column(DateTime, nullable=True, comment="QR code expiry time")
    status = Column(String, default="Close", comment="Session status")
    
    # Foreign keys
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "session_type IN ('theory', 'practice', 'seminar')", 
            name="teaching_sessions_type_check"
        ),
        CheckConstraint(
            "status IN ('Open', 'Close')", 
            name="teaching_sessions_status_check"
        ),
    )
    
    # Relationships
    class_ = relationship("Class", back_populates="teaching_sessions", lazy="select")
    attendances = relationship("Attendance", back_populates="session", lazy="select")
    
    def __repr__(self):
        return f"<TeachingSession(date={self.session_date}, class_id={self.class_id}, status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.status == "Open"
    
    @property
    def is_qr_valid(self) -> bool:
        """Check if QR code is still valid."""
        if not self.qr_code or not self.qr_expired_at:
            return False
        from datetime import datetime
        return datetime.utcnow() < self.qr_expired_at
    
    @property
    def attendance_count(self) -> int:
        """Get total attendance count for this session."""
        return len([att for att in self.attendances if att.status in ['present', 'late']])
