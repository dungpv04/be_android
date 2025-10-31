from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import secrets
from supabase import Client
from app.models import Class, TeachingSession, Attendance, ClassStudent
from app.repositories import (
    ClassRepository, TeachingSessionRepository, AttendanceRepository,
    ClassStudentRepository
)
from app.services.base import BaseService


class ClassService(BaseService[Class]):
    """Service for Class business logic."""
    
    def __init__(self, supabase: Client):
        repository = ClassRepository(supabase)
        super().__init__(repository)
    
    async def get_by_code(self, code: str) -> Optional[Class]:
        """Get class by code."""
        return await self.repository.get_by_code(code)
    
    async def get_by_teacher(self, teacher_id: int) -> List[Class]:
        """Get classes by teacher."""
        return await self.repository.get_by_teacher(teacher_id)
    
    async def get_by_subject(self, subject_id: int) -> List[Class]:
        """Get classes by subject."""
        return await self.repository.get_by_subject(subject_id)
    
    async def get_active_classes(self) -> List[Class]:
        """Get active classes."""
        return await self.repository.get_active_classes()
    
    async def get_classes_with_details(self, page: int = 1, limit: int = 10, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get classes with joined data and student count."""
        return await self.repository.get_classes_with_details(page, limit, filters or {})
    
    async def create(self, data: Dict[str, Any]) -> Optional[Class]:
        """Create class with validation."""
        # Check if code is unique
        existing = await self.repository.get_by_code(data.get("code"))
        if existing:
            raise ValueError("Class code already exists")
        
        return await self.repository.create(data)


class TeachingSessionService(BaseService[TeachingSession]):
    """Service for Teaching Session business logic."""
    
    def __init__(self, supabase: Client):
        repository = TeachingSessionRepository(supabase)
        super().__init__(repository)
    
    async def get_by_class(self, class_id: int) -> List[TeachingSession]:
        """Get teaching sessions by class."""
        return await self.repository.get_by_class(class_id)
    
    async def get_open_sessions(self) -> List[TeachingSession]:
        """Get open teaching sessions."""
        return await self.repository.get_open_sessions()
    
    async def generate_qr_code(self, session_id: int, expiry_minutes: int = 30) -> Optional[str]:
        """Generate QR code for a teaching session."""
        try:
            # Generate a secure random token
            qr_token = secrets.token_urlsafe(32)
            qr_code = f"attendance://{session_id}/{qr_token}"
            
            # Set expiry time
            expired_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
            
            # Update session with QR code
            updated_session = await self.repository.update_qr_code(session_id, qr_code, expired_at)
            
            return qr_code if updated_session else None
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
    
    async def validate_qr_code(self, session_id: int, qr_code: str) -> bool:
        """Validate QR code for attendance."""
        try:
            session = await self.repository.get_by_id(session_id)
            if not session:
                return False
            
            # Check if QR code matches
            if session.qr_code != qr_code:
                return False
            
            # Check if QR code is not expired
            if session.qr_expired_at and datetime.utcnow() > session.qr_expired_at:
                return False
            
            return True
        except Exception as e:
            print(f"Error validating QR code: {e}")
            return False


class AttendanceService(BaseService[Attendance]):
    """Service for Attendance business logic."""
    
    def __init__(self, supabase: Client):
        repository = AttendanceRepository(supabase)
        super().__init__(repository)
        self.session_repository = TeachingSessionRepository(supabase)
    
    async def get_by_session(self, session_id: int) -> List[Attendance]:
        """Get attendance by session."""
        return await self.repository.get_by_session(session_id)
    
    async def get_by_student(self, student_id: int) -> List[Attendance]:
        """Get attendance by student."""
        return await self.repository.get_by_student(student_id)
    
    async def mark_attendance_by_qr(self, session_id: int, student_id: int, qr_code: str, 
                                   ip_address: str = None, user_agent: str = None) -> Optional[Attendance]:
        """Mark attendance using QR code."""
        try:
            # Validate QR code
            session_service = TeachingSessionService(self.repository.supabase)
            if not await session_service.validate_qr_code(session_id, qr_code):
                raise ValueError("Invalid or expired QR code")
            
            # Check if already marked attendance
            existing = await self.repository.get_by_session_and_student(session_id, student_id)
            if existing:
                raise ValueError("Attendance already marked for this session")
            
            # Mark attendance
            attendance_data = {
                "session_id": session_id,
                "student_id": student_id,
                "status": "present",
                "attendance_time": datetime.utcnow().isoformat(),
                "confidence_score": 1.0,  # QR code attendance has full confidence
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            return await self.repository.create(attendance_data)
        except Exception as e:
            print(f"Error marking attendance by QR: {e}")
            return None
    
    async def mark_attendance_manual(self, session_id: int, student_id: int, status: str) -> Optional[Attendance]:
        """Mark attendance manually (for teachers)."""
        try:
            # Check if already marked attendance
            existing = await self.repository.get_by_session_and_student(session_id, student_id)
            if existing:
                # Update existing attendance
                return await self.repository.update(existing.id, {"status": status})
            
            # Create new attendance record
            attendance_data = {
                "session_id": session_id,
                "student_id": student_id,
                "status": status,
                "attendance_time": datetime.utcnow().isoformat()
            }
            
            return await self.repository.create(attendance_data)
        except Exception as e:
            print(f"Error marking attendance manually: {e}")
            return None
    
    async def get_attendance_statistics(self, class_id: int, start_date, end_date) -> Dict[str, Any]:
        """Get attendance statistics for a class."""
        return await self.repository.get_attendance_statistics(class_id, start_date, end_date)


class ClassStudentService(BaseService[ClassStudent]):
    """Service for Class Student business logic."""
    
    def __init__(self, supabase: Client):
        repository = ClassStudentRepository(supabase)
        super().__init__(repository)
    
    async def get_by_class(self, class_id: int) -> List[ClassStudent]:
        """Get class students by class."""
        return await self.repository.get_by_class(class_id)
    
    async def get_by_student(self, student_id: int) -> List[ClassStudent]:
        """Get class students by student."""
        return await self.repository.get_by_student(student_id)
    
    async def get_active_enrollments(self, class_id: int) -> List[ClassStudent]:
        """Get active enrollments for a class."""
        return await self.repository.get_active_enrollments(class_id)
    
    async def get_class_students_with_details(self, class_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get class students with detailed student information."""
        return await self.repository.get_class_students_with_details(class_id, active_only)
    
    async def get_student_classes_with_details(self, student_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get classes for a specific student with detailed information."""
        return await self.repository.get_student_classes_with_details(student_id, active_only)
    
    async def enroll_student(self, class_id: int, student_id: int) -> Optional[ClassStudent]:
        """Enroll a student in a class."""
        return await self.repository.enroll_student(class_id, student_id)
    
    async def unenroll_student(self, class_id: int, student_id: int) -> bool:
        """Unenroll a student from a class."""
        return await self.repository.unenroll_student(class_id, student_id)
