from typing import Optional, List, Dict, Any
from supabase import Client
from app.models import Student, Teacher
from app.repositories.base import BaseRepository
from app.schemas.users import TeacherCreate, StudentCreate


class UserRepository:
    """Repository for common user operations across students and teachers."""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.student_repo = None  # Will be initialized when needed to avoid circular import
        self.teacher_repo = None  # Will be initialized when needed to avoid circular import
    
    def _get_student_repo(self):
        """Lazy initialization of student repository."""
        if self.student_repo is None:
            self.student_repo = StudentRepository(self.supabase)
        return self.student_repo
    
    def _get_teacher_repo(self):
        """Lazy initialization of teacher repository."""
        if self.teacher_repo is None:
            self.teacher_repo = TeacherRepository(self.supabase)
        return self.teacher_repo
    
    async def check_email_exists(self, email: str) -> bool:
        """Check if email exists in students or teachers table."""
        try:
            # Check students
            student_response = self.supabase.table("students").select("id").eq("email", email).execute()
            if student_response.data:
                return True
            
            # Check teachers
            teacher_response = self.supabase.table("teachers").select("id").eq("email", email).execute()
            return bool(teacher_response.data)
        except Exception as e:
            print(f"Error checking email existence: {e}")
            return False
    
    async def check_student_code_exists(self, student_code: str) -> bool:
        """Check if student code exists."""
        try:
            response = self.supabase.table("students").select("id").eq("student_code", student_code).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error checking student code existence: {e}")
            return False


class StudentRepository(BaseRepository[Student]):
    """Repository for Student operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "students", Student)
    
    async def get_by_student_code(self, student_code: str) -> Optional[Student]:
        """Get student by student code."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("student_code", student_code).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting student by code: {e}")
            return None
    
    async def get_by_auth_id(self, auth_id: str) -> Optional[Student]:
        """Get student by auth ID."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("auth_id", auth_id).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting student by auth ID: {e}")
            return None
    
    async def get_by_faculty(self, faculty_id: int) -> List[Student]:
        """Get students by faculty ID."""
        return await self.find_by_field("faculty_id", faculty_id)
    
    async def get_by_major(self, major_id: int) -> List[Student]:
        """Get students by major ID."""
        return await self.find_by_field("major_id", major_id)
    
    async def get_by_cohort(self, cohort_id: int) -> List[Student]:
        """Get students by cohort ID."""
        return await self.find_by_field("cohort_id", cohort_id)
    
    async def get_by_class_name(self, class_name: str) -> List[Student]:
        """Get students by class name."""
        return await self.find_by_field("class_name", class_name)
    
    async def search_by_name(self, name: str) -> List[Student]:
        """Search students by name."""
        try:
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .ilike("full_name", f"%{name}%")
                       .execute())
            
            return [self.model_class(**item) for item in response.data] if response.data else []
        except Exception as e:
            print(f"Error searching students by name: {e}")
            return []


class TeacherRepository(BaseRepository[Teacher]):
    """Repository for Teacher operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "teachers", Teacher)
    
    async def get_by_teacher_code(self, teacher_code: str) -> Optional[Teacher]:
        """Get teacher by teacher code."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("teacher_code", teacher_code).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting teacher by code: {e}")
            return None
    
    async def get_by_auth_id(self, auth_id: str) -> Optional[Teacher]:
        """Get teacher by auth ID."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("auth_id", auth_id).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting teacher by auth ID: {e}")
            return None
    
    async def get_by_faculty(self, faculty_id: int) -> List[Teacher]:
        """Get teachers by faculty ID."""
        return await self.find_by_field("faculty_id", faculty_id)
    
    async def get_by_department(self, department_id: int) -> List[Teacher]:
        """Get teachers by department ID."""
        return await self.find_by_field("department_id", department_id)
    
    async def search_by_name(self, name: str) -> List[Teacher]:
        """Search teachers by name."""
        try:
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .ilike("full_name", f"%{name}%")
                       .execute())
            
            return [self.model_class(**item) for item in response.data] if response.data else []
        except Exception as e:
            print(f"Error searching teachers by name: {e}")
            return []
