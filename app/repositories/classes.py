from typing import Optional, List, Dict, Any
from datetime import date, datetime
from supabase import Client
from app.models import Class, TeachingSession, Attendance, ClassStudent
from app.repositories.base import BaseRepository


class ClassRepository(BaseRepository[Class]):
    """Repository for Class operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "classes", Class)
    
    async def get_by_code(self, code: str) -> Optional[Class]:
        """Get class by code."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("code", code).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting class by code: {e}")
            return None
    
    async def get_by_teacher(self, teacher_id: int) -> List[Class]:
        """Get classes by teacher ID."""
        return await self.find_by_field("teacher_id", teacher_id)
    
    async def get_by_subject(self, subject_id: int) -> List[Class]:
        """Get classes by subject ID."""
        return await self.find_by_field("subject_id", subject_id)
    
    async def get_active_classes(self) -> List[Class]:
        """Get all active classes."""
        return await self.find_by_field("status", "active")


class TeachingSessionRepository(BaseRepository[TeachingSession]):
    """Repository for Teaching Session operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "teaching_sessions", TeachingSession)
    
    async def get_by_class(self, class_id: int) -> List[TeachingSession]:
        """Get teaching sessions by class ID."""
        return await self.find_by_field("class_id", class_id)
    
    async def get_by_date(self, session_date: date) -> List[TeachingSession]:
        """Get teaching sessions by date."""
        try:
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .eq("session_date", session_date.isoformat())
                       .execute())
            
            return [self.model_class(**item) for item in response.data] if response.data else []
        except Exception as e:
            print(f"Error getting teaching sessions by date: {e}")
            return []
    
    async def get_by_class_and_date(self, class_id: int, session_date: date) -> List[TeachingSession]:
        """Get teaching sessions by class and date."""
        try:
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .eq("class_id", class_id)
                       .eq("session_date", session_date.isoformat())
                       .execute())
            
            return [self.model_class(**item) for item in response.data] if response.data else []
        except Exception as e:
            print(f"Error getting teaching sessions by class and date: {e}")
            return []
    
    async def get_open_sessions(self) -> List[TeachingSession]:
        """Get all open teaching sessions."""
        return await self.find_by_field("status", "Open")
    
    async def update_qr_code(self, session_id: int, qr_code: str, expired_at: datetime) -> Optional[TeachingSession]:
        """Update QR code for a session."""
        try:
            response = (self.supabase.table(self.table_name)
                       .update({
                           "qr_code": qr_code,
                           "qr_expired_at": expired_at.isoformat()
                       })
                       .eq("id", session_id)
                       .execute())
            
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error updating QR code: {e}")
            return None


class AttendanceRepository(BaseRepository[Attendance]):
    """Repository for Attendance operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "attendances", Attendance)
    
    async def get_by_session(self, session_id: int) -> List[Attendance]:
        """Get attendance by session ID."""
        return await self.find_by_field("session_id", session_id)
    
    async def get_by_student(self, student_id: int) -> List[Attendance]:
        """Get attendance by student ID."""
        return await self.find_by_field("student_id", student_id)
    
    async def get_by_session_and_student(self, session_id: int, student_id: int) -> Optional[Attendance]:
        """Get attendance by session and student."""
        try:
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .eq("session_id", session_id)
                       .eq("student_id", student_id)
                       .execute())
            
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting attendance by session and student: {e}")
            return None
    
    async def get_attendance_statistics(self, class_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get attendance statistics for a class within date range."""
        try:
            # This would require a more complex query, potentially using SQL functions
            # For now, we'll return a basic structure
            sessions = await self.supabase.table("teaching_sessions").select("id").eq("class_id", class_id).gte("session_date", start_date.isoformat()).lte("session_date", end_date.isoformat()).execute()
            
            if not sessions.data:
                return {"total_sessions": 0, "attendance_rate": 0}
            
            session_ids = [s["id"] for s in sessions.data]
            total_sessions = len(session_ids)
            
            # Get total attendances for these sessions
            attendances = []
            for session_id in session_ids:
                session_attendances = await self.get_by_session(session_id)
                attendances.extend(session_attendances)
            
            present_count = len([a for a in attendances if a.status == "present"])
            total_possible = total_sessions * len(set(a.student_id for a in attendances)) if attendances else 0
            
            attendance_rate = (present_count / total_possible * 100) if total_possible > 0 else 0
            
            return {
                "total_sessions": total_sessions,
                "total_attendances": len(attendances),
                "present_count": present_count,
                "attendance_rate": round(attendance_rate, 2)
            }
        except Exception as e:
            print(f"Error getting attendance statistics: {e}")
            return {"total_sessions": 0, "attendance_rate": 0}


class ClassStudentRepository(BaseRepository[ClassStudent]):
    """Repository for Class Student operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "class_students", ClassStudent)
    
    async def get_by_class(self, class_id: int) -> List[ClassStudent]:
        """Get class students by class ID."""
        return await self.find_by_field("class_id", class_id)
    
    async def get_by_student(self, student_id: int) -> List[ClassStudent]:
        """Get class students by student ID."""
        return await self.find_by_field("student_id", student_id)
    
    async def get_active_enrollments(self, class_id: int) -> List[ClassStudent]:
        """Get active enrollments for a class."""
        try:
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .eq("class_id", class_id)
                       .eq("status", "active")
                       .execute())
            
            return [self.model_class(**item) for item in response.data] if response.data else []
        except Exception as e:
            print(f"Error getting active enrollments: {e}")
            return []
    
    async def enroll_student(self, class_id: int, student_id: int) -> Optional[ClassStudent]:
        """Enroll a student in a class."""
        try:
            # Check if already enrolled
            existing = await self.supabase.table(self.table_name).select("*").eq("class_id", class_id).eq("student_id", student_id).execute()
            
            if existing.data:
                # Update status to active if inactive
                return await self.update(existing.data[0]["id"], {"status": "active"})
            else:
                # Create new enrollment
                return await self.create({
                    "class_id": class_id,
                    "student_id": student_id,
                    "status": "active"
                })
        except Exception as e:
            print(f"Error enrolling student: {e}")
            return None
    
    async def unenroll_student(self, class_id: int, student_id: int) -> bool:
        """Unenroll a student from a class."""
        try:
            response = (self.supabase.table(self.table_name)
                       .update({"status": "inactive"})
                       .eq("class_id", class_id)
                       .eq("student_id", student_id)
                       .execute())
            
            return response.data is not None
        except Exception as e:
            print(f"Error unenrolling student: {e}")
            return False
