"""
Attendance and face recognition models.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Numeric, Text, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class Attendance(BaseModel):
    """Attendance record model."""
    
    __tablename__ = "attendances"
    
    attendance_time = Column(DateTime, default=datetime.utcnow, comment="Time of attendance marking")
    status = Column(String, nullable=True, comment="Attendance status")
    confidence_score = Column(Numeric, nullable=True, comment="Face recognition confidence")
    ip_address = Column(String, nullable=True, comment="Client IP address")
    user_agent = Column(Text, nullable=True, comment="Client user agent")
    
    # Foreign keys
    session_id = Column(Integer, ForeignKey("teaching_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('present', 'absent', 'late')", 
            name="attendances_status_check"
        ),
    )
    
    # Relationships
    session = relationship("TeachingSession", back_populates="attendances", lazy="select")
    student = relationship("Student", back_populates="attendances", lazy="select")
    
    def __repr__(self):
        return f"<Attendance(session_id={self.session_id}, student_id={self.student_id}, status='{self.status}')>"
    
    @property
    def is_present(self) -> bool:
        """Check if student was present (present or late)."""
        return self.status in ['present', 'late']
    
    @property
    def is_late(self) -> bool:
        """Check if student was late."""
        return self.status == 'late'
    
    def get_attendance_duration(self) -> int:
        """Get minutes between session start and attendance time."""
        if not self.session or not self.attendance_time:
            return 0
        
        # Combine session date and start time
        session_start = datetime.combine(
            self.session.session_date, 
            self.session.start_time
        )
        
        # Calculate difference in minutes
        diff = self.attendance_time - session_start
        return int(diff.total_seconds() / 60)


class FaceTemplate(BaseModel):
    """Face recognition template model."""
    
    __tablename__ = "face_templates"
    
    image_path = Column(Text, nullable=False, comment="Path to face image")
    face_encoding = Column(JSONB, nullable=False, comment="Face encoding data")
    is_primary = Column(Boolean, default=False, comment="Primary face template")
    
    # Foreign keys
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Relationships
    student = relationship("Student", back_populates="face_templates", lazy="select")
    
    def __repr__(self):
        return f"<FaceTemplate(student_id={self.student_id}, primary={self.is_primary})>"
    
    @property
    def encoding_vector(self) -> list:
        """Get face encoding as list."""
        if isinstance(self.face_encoding, dict) and 'encoding' in self.face_encoding:
            return self.face_encoding['encoding']
        return []
    
    def set_encoding_vector(self, encoding: list):
        """Set face encoding from list."""
        self.face_encoding = {
            'encoding': encoding,
            'version': '1.0',
            'created_at': datetime.utcnow().isoformat()
        }
    
    def calculate_similarity(self, other_encoding: list) -> float:
        """Calculate similarity with another face encoding."""
        try:
            import numpy as np
            current_encoding = np.array(self.encoding_vector)
            other_encoding = np.array(other_encoding)
            
            # Calculate euclidean distance
            distance = np.linalg.norm(current_encoding - other_encoding)
            
            # Convert to similarity score (0-1, higher is more similar)
            similarity = max(0, 1 - (distance / 2))
            return float(similarity)
        except Exception:
            return 0.0
