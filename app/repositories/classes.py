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
    
    async def get_classes_with_details(self, page: int = 1, limit: int = 10, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get classes with joined data and student count."""
        try:
            # Use the fallback method which works with standard Supabase queries
            return await self._get_classes_with_details_fallback(page, limit, filters)
            
        except Exception as e:
            print(f"Error getting classes with details: {e}")
            # Ultimate fallback to basic method
            return await self.get_all(page, limit)
    
    async def _get_classes_with_details_fallback(self, page: int, limit: int, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback method using separate queries with comprehensive filtering."""
        try:
            # Build query with filters
            offset = (page - 1) * limit
            
            # Start with base query
            query = self.supabase.table(self.table_name).select("*", count="exact")
            
            # Add filters
            query = query.eq("status", "active")  # Default filter for active classes
            
            if filters:
                if filters.get("teacher_id"):
                    query = query.eq("teacher_id", filters["teacher_id"])
                if filters.get("subject_id"):
                    query = query.eq("subject_id", filters["subject_id"])
                if filters.get("semester_id"):
                    query = query.eq("semester_id", filters["semester_id"])
                if filters.get("faculty_id"):
                    query = query.eq("faculty_id", filters["faculty_id"])
                if filters.get("department_id"):
                    query = query.eq("department_id", filters["department_id"])
                if filters.get("major_id"):
                    query = query.eq("major_id", filters["major_id"])
                if filters.get("cohort_id"):
                    query = query.eq("cohort_id", filters["cohort_id"])
                if filters.get("academic_year_id"):
                    query = query.eq("academic_year_id", filters["academic_year_id"])
                if filters.get("study_phase_id"):
                    query = query.eq("study_phase_id", filters["study_phase_id"])
            
            # Execute query with pagination
            response = query.range(offset, offset + limit - 1).execute()
            
            if not response.data:
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "limit": limit,
                    "total_pages": 0
                }
            
            # Get total count
            total = response.count if response.count else 0
            
            # Convert to model instances
            classes = [self.model_class(**item) for item in response.data]
            
            # Enhance each class with related data
            enhanced_classes = []
            for cls in classes:
                class_dict = cls.model_dump()
                
                # Get related data from other tables
                if cls.faculty_id:
                    faculty_response = self.supabase.table("faculties").select("name").eq("id", cls.faculty_id).execute()
                    class_dict["faculty_name"] = faculty_response.data[0]["name"] if faculty_response.data else None
                
                if cls.department_id:
                    dept_response = self.supabase.table("departments").select("name").eq("id", cls.department_id).execute()
                    class_dict["department_name"] = dept_response.data[0]["name"] if dept_response.data else None
                
                if cls.major_id:
                    major_response = self.supabase.table("majors").select("name").eq("id", cls.major_id).execute()
                    class_dict["major_name"] = major_response.data[0]["name"] if major_response.data else None
                
                if cls.subject_id:
                    subject_response = self.supabase.table("subjects").select("name, code").eq("id", cls.subject_id).execute()
                    if subject_response.data:
                        class_dict["subject_name"] = subject_response.data[0]["name"]
                        class_dict["subject_code"] = subject_response.data[0]["code"]
                
                if cls.teacher_id:
                    teacher_response = self.supabase.table("teachers").select("full_name, teacher_code").eq("id", cls.teacher_id).execute()
                    if teacher_response.data:
                        class_dict["teacher_name"] = teacher_response.data[0]["full_name"]
                        class_dict["teacher_code"] = teacher_response.data[0]["teacher_code"]
                
                if cls.cohort_id:
                    cohort_response = self.supabase.table("cohorts").select("name").eq("id", cls.cohort_id).execute()
                    class_dict["cohort_name"] = cohort_response.data[0]["name"] if cohort_response.data else None
                
                if cls.academic_year_id:
                    ay_response = self.supabase.table("academic_years").select("name").eq("id", cls.academic_year_id).execute()
                    class_dict["academic_year_name"] = ay_response.data[0]["name"] if ay_response.data else None
                
                if cls.semester_id:
                    sem_response = self.supabase.table("semesters").select("name").eq("id", cls.semester_id).execute()
                    class_dict["semester_name"] = sem_response.data[0]["name"] if sem_response.data else None
                
                if cls.study_phase_id:
                    sp_response = self.supabase.table("study_phases").select("name").eq("id", cls.study_phase_id).execute()
                    class_dict["study_phase_name"] = sp_response.data[0]["name"] if sp_response.data else None
                
                # Get student count
                student_count_response = self.supabase.table("class_students").select("id").eq("class_id", cls.id).eq("status", "active").execute()
                class_dict["student_count"] = len(student_count_response.data) if student_count_response.data else 0
                
                enhanced_classes.append(class_dict)
            
            return {
                "items": enhanced_classes,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
            
        except Exception as e:
            print(f"Error in fallback method: {e}")
            return await self.get_all(page, limit)


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
    
    async def get_session_attendance_with_details(self, session_id: int) -> List[Dict[str, Any]]:
        """Get attendance for a session with detailed joined information."""
        try:
            # Get attendance records for the session
            attendance_response = (self.supabase.table(self.table_name)
                                 .select("*")
                                 .eq("session_id", session_id)
                                 .execute())
            
            if not attendance_response.data:
                return []
            
            # Get session details
            session_response = (self.supabase.table("teaching_sessions")
                              .select("*")
                              .eq("id", session_id)
                              .execute())
            
            session_data = session_response.data[0] if session_response.data else {}
            class_id = session_data.get("class_id")
            
            # Get class details
            class_response = (self.supabase.table("classes")
                            .select("*")
                            .eq("id", class_id)
                            .execute()) if class_id else None
            
            class_data = class_response.data[0] if class_response and class_response.data else {}
            
            # Get subject details
            subject_data = {}
            if class_data.get("subject_id"):
                subject_response = (self.supabase.table("subjects")
                                  .select("name, code")
                                  .eq("id", class_data["subject_id"])
                                  .execute())
                subject_data = subject_response.data[0] if subject_response.data else {}
            
            # Get teacher details
            teacher_data = {}
            if class_data.get("teacher_id"):
                teacher_response = (self.supabase.table("teachers")
                                  .select("full_name, teacher_code")
                                  .eq("id", class_data["teacher_id"])
                                  .execute())
                teacher_data = teacher_response.data[0] if teacher_response.data else {}
            
            # Process each attendance record
            result = []
            for attendance in attendance_response.data:
                # Get student details
                student_response = (self.supabase.table("students")
                                  .select("full_name, student_code, phone, hometown, class_name")
                                  .eq("id", attendance["student_id"])
                                  .execute())
                
                student_data = student_response.data[0] if student_response.data else {}
                
                # Combine all data
                detailed_attendance = {
                    # Attendance details
                    **attendance,
                    # Student details
                    "student_name": student_data.get("full_name"),
                    "student_code": student_data.get("student_code"),
                    "student_phone": student_data.get("phone"),
                    "student_hometown": student_data.get("hometown"),
                    "student_class_name": student_data.get("class_name"),
                    # Session details
                    "session_date": session_data.get("session_date"),
                    "session_start_time": session_data.get("start_time"),
                    "session_end_time": session_data.get("end_time"),
                    "session_type": session_data.get("session_type"),
                    "session_status": session_data.get("status"),
                    # Class details
                    "class_id": class_data.get("id"),
                    "class_name": class_data.get("name"),
                    "class_code": class_data.get("code"),
                    # Subject details
                    "subject_name": subject_data.get("name"),
                    "subject_code": subject_data.get("code"),
                    # Teacher details
                    "teacher_name": teacher_data.get("full_name"),
                    "teacher_code": teacher_data.get("teacher_code")
                }
                
                result.append(detailed_attendance)
            
            return result
            
        except Exception as e:
            print(f"Error getting session attendance with details: {e}")
            return []
    
    async def get_session_student_attendance_with_details(self, session_id: int, student_id: int) -> List[Dict[str, Any]]:
        """Get attendance for a specific student in a session with detailed joined information."""
        try:
            # Get attendance records for the specific student in the session
            attendance_response = (self.supabase.table(self.table_name)
                                 .select("*")
                                 .eq("session_id", session_id)
                                 .eq("student_id", student_id)
                                 .execute())
            
            if not attendance_response.data:
                return []
            
            # Get session details
            session_response = (self.supabase.table("teaching_sessions")
                              .select("*")
                              .eq("id", session_id)
                              .execute())
            
            session_data = session_response.data[0] if session_response.data else {}
            class_id = session_data.get("class_id")
            
            # Get class details
            class_response = (self.supabase.table("classes")
                            .select("*")
                            .eq("id", class_id)
                            .execute()) if class_id else None
            
            class_data = class_response.data[0] if class_response and class_response.data else {}
            
            # Get subject details
            subject_data = {}
            if class_data.get("subject_id"):
                subject_response = (self.supabase.table("subjects")
                                  .select("name, code")
                                  .eq("id", class_data["subject_id"])
                                  .execute())
                subject_data = subject_response.data[0] if subject_response.data else {}
            
            # Get teacher details
            teacher_data = {}
            if class_data.get("teacher_id"):
                teacher_response = (self.supabase.table("teachers")
                                  .select("full_name, teacher_code")
                                  .eq("id", class_data["teacher_id"])
                                  .execute())
                teacher_data = teacher_response.data[0] if teacher_response.data else {}
            
            # Get student details
            student_response = (self.supabase.table("students")
                              .select("full_name, student_code, phone, hometown, class_name")
                              .eq("id", student_id)
                              .execute())
            
            student_data = student_response.data[0] if student_response.data else {}
            
            # Get faculty details
            faculty_data = {}
            if class_data.get("faculty_id"):
                faculty_response = (self.supabase.table("faculties")
                                  .select("name")
                                  .eq("id", class_data["faculty_id"])
                                  .execute())
                faculty_data = faculty_response.data[0] if faculty_response.data else {}
            
            # Get department details
            department_data = {}
            if class_data.get("department_id"):
                department_response = (self.supabase.table("departments")
                                     .select("name")
                                     .eq("id", class_data["department_id"])
                                     .execute())
                department_data = department_response.data[0] if department_response.data else {}
            
            # Get major details
            major_data = {}
            if class_data.get("major_id"):
                major_response = (self.supabase.table("majors")
                                .select("name")
                                .eq("id", class_data["major_id"])
                                .execute())
                major_data = major_response.data[0] if major_response.data else {}
            
            # Get cohort details
            cohort_data = {}
            if class_data.get("cohort_id"):
                cohort_response = (self.supabase.table("cohorts")
                                 .select("name")
                                 .eq("id", class_data["cohort_id"])
                                 .execute())
                cohort_data = cohort_response.data[0] if cohort_response.data else {}
            
            # Get academic year details
            academic_year_data = {}
            if class_data.get("academic_year_id"):
                academic_year_response = (self.supabase.table("academic_years")
                                        .select("name")
                                        .eq("id", class_data["academic_year_id"])
                                        .execute())
                academic_year_data = academic_year_response.data[0] if academic_year_response.data else {}
            
            # Get semester details
            semester_data = {}
            if class_data.get("semester_id"):
                semester_response = (self.supabase.table("semesters")
                                   .select("name")
                                   .eq("id", class_data["semester_id"])
                                   .execute())
                semester_data = semester_response.data[0] if semester_response.data else {}
            
            # Get study phase details
            study_phase_data = {}
            if class_data.get("study_phase_id"):
                study_phase_response = (self.supabase.table("study_phases")
                                      .select("name")
                                      .eq("id", class_data["study_phase_id"])
                                      .execute())
                study_phase_data = study_phase_response.data[0] if study_phase_response.data else {}
            
            # Process each attendance record
            result = []
            for attendance in attendance_response.data:
                # Combine all data
                detailed_attendance = {
                    # Attendance details
                    **attendance,
                    # Student details
                    "student_name": student_data.get("full_name"),
                    "student_code": student_data.get("student_code"),
                    "student_phone": student_data.get("phone"),
                    "student_hometown": student_data.get("hometown"),
                    "student_class_name": student_data.get("class_name"),
                    # Session details
                    "session_date": session_data.get("session_date"),
                    "session_start_time": session_data.get("start_time"),
                    "session_end_time": session_data.get("end_time"),
                    "session_type": session_data.get("session_type"),
                    "session_status": session_data.get("status"),
                    # Class details
                    "class_id": class_data.get("id"),
                    "class_name": class_data.get("name"),
                    "class_code": class_data.get("code"),
                    # Subject details
                    "subject_name": subject_data.get("name"),
                    "subject_code": subject_data.get("code"),
                    # Teacher details
                    "teacher_name": teacher_data.get("full_name"),
                    "teacher_code": teacher_data.get("teacher_code"),
                    # Additional FK details
                    "faculty_name": faculty_data.get("name"),
                    "department_name": department_data.get("name"),
                    "major_name": major_data.get("name"),
                    "cohort_name": cohort_data.get("name"),
                    "academic_year_name": academic_year_data.get("name"),
                    "semester_name": semester_data.get("name"),
                    "study_phase_name": study_phase_data.get("name")
                }
                
                result.append(detailed_attendance)
            
            return result
            
        except Exception as e:
            print(f"Error getting session student attendance with details: {e}")
            return []
    
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
    
    async def get_class_students_with_details(self, class_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get class students with detailed student information."""
        try:
            # Get class students
            cs_query = self.supabase.table(self.table_name).select("*").eq("class_id", class_id)
            if active_only:
                cs_query = cs_query.eq("status", "active")
            
            cs_response = cs_query.execute()
            
            if not cs_response.data:
                return []
            
            # Get student details for each enrollment
            result = []
            for enrollment in cs_response.data:
                student_response = (self.supabase.table("students")
                                  .select("full_name, student_code, phone, hometown, class_name")
                                  .eq("id", enrollment["student_id"])
                                  .execute())
                
                if student_response.data:
                    student = student_response.data[0]
                    result.append({
                        **enrollment,
                        "student_name": student["full_name"],
                        "student_code": student["student_code"],
                        "student_email": None,  # Set to None since email doesn't exist
                        "student_phone": student.get("phone"),
                        "student_hometown": student.get("hometown"),
                        "class_name": student.get("class_name")
                    })
            
            return result
            
        except Exception as e:
            print(f"Error getting class students with details: {e}")
            return []
    
    async def get_student_classes_with_details(self, student_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get classes for a specific student with detailed information."""
        try:
            # Get class enrollments for the student
            cs_query = self.supabase.table(self.table_name).select("*").eq("student_id", student_id)
            if active_only:
                cs_query = cs_query.eq("status", "active")
            
            cs_response = cs_query.execute()
            
            if not cs_response.data:
                return []
            
            # Get detailed class information for each enrollment
            result = []
            for enrollment in cs_response.data:
                class_id = enrollment["class_id"]
                
                # Get class details with joins
                class_response = (self.supabase.table("classes")
                                .select("*")
                                .eq("id", class_id)
                                .execute())
                
                if not class_response.data:
                    continue
                
                class_data = class_response.data[0]
                
                # Get faculty details
                faculty_response = (self.supabase.table("faculties")
                                  .select("name")
                                  .eq("id", class_data.get("faculty_id"))
                                  .execute())
                faculty_name = faculty_response.data[0]["name"] if faculty_response.data else None
                
                # Get department details
                department_response = (self.supabase.table("departments")
                                     .select("name")
                                     .eq("id", class_data.get("department_id"))
                                     .execute())
                department_name = department_response.data[0]["name"] if department_response.data else None
                
                # Get major details
                major_response = (self.supabase.table("majors")
                                .select("name")
                                .eq("id", class_data.get("major_id"))
                                .execute())
                major_name = major_response.data[0]["name"] if major_response.data else None
                
                # Get subject details
                subject_response = (self.supabase.table("subjects")
                                  .select("name, code")
                                  .eq("id", class_data.get("subject_id"))
                                  .execute())
                subject_name = subject_response.data[0]["name"] if subject_response.data else None
                subject_code = subject_response.data[0]["code"] if subject_response.data else None
                
                # Get teacher details
                teacher_response = (self.supabase.table("teachers")
                                  .select("full_name, teacher_code")
                                  .eq("id", class_data.get("teacher_id"))
                                  .execute())
                teacher_name = teacher_response.data[0]["full_name"] if teacher_response.data else None
                teacher_code = teacher_response.data[0]["teacher_code"] if teacher_response.data else None
                
                # Get cohort details
                cohort_response = (self.supabase.table("cohorts")
                                 .select("name")
                                 .eq("id", class_data.get("cohort_id"))
                                 .execute())
                cohort_name = cohort_response.data[0]["name"] if cohort_response.data else None
                
                # Get academic year details
                academic_year_response = (self.supabase.table("academic_years")
                                        .select("name")
                                        .eq("id", class_data.get("academic_year_id"))
                                        .execute())
                academic_year_name = academic_year_response.data[0]["name"] if academic_year_response.data else None
                
                # Get semester details
                semester_response = (self.supabase.table("semesters")
                                   .select("name")
                                   .eq("id", class_data.get("semester_id"))
                                   .execute())
                semester_name = semester_response.data[0]["name"] if semester_response.data else None
                
                # Get study phase details
                study_phase_response = (self.supabase.table("study_phases")
                                      .select("name")
                                      .eq("id", class_data.get("study_phase_id"))
                                      .execute())
                study_phase_name = study_phase_response.data[0]["name"] if study_phase_response.data else None
                
                # Get student count for this class
                student_count_response = (self.supabase.table(self.table_name)
                                        .select("*", count="exact")
                                        .eq("class_id", class_id)
                                        .eq("status", "active")
                                        .execute())
                student_count = student_count_response.count if student_count_response.count else 0
                
                # Combine all data
                result.append({
                    **class_data,
                    "faculty_name": faculty_name,
                    "department_name": department_name,
                    "major_name": major_name,
                    "subject_name": subject_name,
                    "subject_code": subject_code,
                    "teacher_name": teacher_name,
                    "teacher_code": teacher_code,
                    "cohort_name": cohort_name,
                    "academic_year_name": academic_year_name,
                    "semester_name": semester_name,
                    "study_phase_name": study_phase_name,
                    "student_count": student_count,
                    # Enrollment details
                    "enrollment_id": enrollment["id"],
                    "enrolled_at": enrollment["enrolled_at"],
                    "enrollment_status": enrollment["status"]
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting student classes with details: {e}")
            return []
    
    async def enroll_student(self, class_id: int, student_id: int) -> Optional[ClassStudent]:
        """Enroll a student in a class."""
        try:
            # Check if already enrolled
            existing = (self.supabase.table(self.table_name)
                       .select("*")
                       .eq("class_id", class_id)
                       .eq("student_id", student_id)
                       .execute())
            
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
