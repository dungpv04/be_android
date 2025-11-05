from typing import Optional, List, Dict, Any
from supabase import Client
from app.core.database import get_supabase_admin
from app.models import Student, Teacher
from app.repositories import StudentRepository, TeacherRepository
from app.services.base import BaseService
from app.schemas import StudentCreate, TeacherCreate


class StudentService(BaseService[Student]):
    """Service for Student business logic."""
    
    def __init__(self, supabase: Client):
        repository = StudentRepository(supabase)
        super().__init__(repository)
        self.supabase = supabase
    
    async def create_student_with_auth(self, student_data: StudentCreate) -> Optional[Student]:
        """Create a student with Supabase authentication."""
        try:
            # Create user in Supabase Auth
            from app.core.auth import auth_service
            auth_response = await auth_service.create_user_with_supabase(
                email=student_data.email,
                password=student_data.password,
                user_metadata={
                    "full_name": student_data.full_name,
                    "user_type": "student"
                }
            )
            
            if not auth_response or not auth_response.get("user"):
                return None
            
            # Create student record
            student_dict = student_data.model_dump(exclude={"password"})
            student_dict["auth_id"] = auth_response["user"].id
            
            return await self.repository.create(student_dict)
            
        except Exception as e:
            print(f"Error creating student with auth: {e}")
            return None
    
    async def get_by_student_code(self, student_code: str) -> Optional[Student]:
        """Get student by student code."""
        return await self.repository.get_by_student_code(student_code)
    
    async def get_by_auth_id(self, auth_id: str) -> Optional[Student]:
        """Get student by auth ID."""
        return await self.repository.get_by_auth_id(auth_id)
    
    async def get_by_faculty(self, faculty_id: int) -> List[Student]:
        """Get students by faculty."""
        return await self.repository.get_by_faculty(faculty_id)
    
    async def get_by_major(self, major_id: int) -> List[Student]:
        """Get students by major."""
        return await self.repository.get_by_major(major_id)
    
    async def get_by_cohort(self, cohort_id: int) -> List[Student]:
        """Get students by cohort."""
        return await self.repository.get_by_cohort(cohort_id)
    
    async def get_by_class_name(self, class_name: str) -> List[Student]:
        """Get students by class name."""
        return await self.repository.get_by_class_name(class_name)
    
    async def search_by_name(self, name: str) -> List[Student]:
        """Search students by name."""
        return await self.repository.search_by_name(name)
    
    async def create(self, data: Dict[str, Any]) -> Optional[Student]:
        """Create student with validation."""
        # Check if student code is unique
        existing = await self.repository.get_by_student_code(data.get("student_code"))
        if existing:
            raise ValueError("Student code already exists")
        
        return await self.repository.create(data)


class TeacherService(BaseService[Teacher]):
    """Service for Teacher business logic."""
    
    def __init__(self, supabase: Client):
        repository = TeacherRepository(supabase)
        super().__init__(repository)
        self.supabase = supabase
    
    async def create_teacher_with_auth(self, teacher_data: TeacherCreate) -> Optional[Teacher]:
        """Create a teacher with Supabase authentication."""
        try:
            # Create user in Supabase Auth
            from app.core.auth import auth_service
            print(f"Creating auth user for teacher: {teacher_data.email}")
            
            auth_response = await auth_service.create_user_with_supabase(
                email=teacher_data.email,
                password=teacher_data.password,
                user_metadata={
                    "full_name": teacher_data.full_name,
                    "user_type": "teacher"
                }
            )
            
            if not auth_response or not auth_response.get("user"):
                print("Failed to create auth user")
                return None
            
            print(f"Auth user created with ID: {auth_response['user'].id}")
            
            # Create teacher record
            teacher_dict = teacher_data.model_dump(exclude={"password"})
            teacher_dict["auth_id"] = auth_response["user"].id
            
            print(f"Creating teacher profile with data: {teacher_dict}")
            teacher = await self.repository.create(teacher_dict)
            
            if teacher:
                print(f"Teacher profile created successfully with ID: {teacher.id}")
            else:
                print("Failed to create teacher profile")
            
            return teacher
            
        except Exception as e:
            print(f"Error creating teacher with auth: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_by_teacher_code(self, teacher_code: str) -> Optional[Teacher]:
        """Get teacher by teacher code."""
        return await self.repository.get_by_teacher_code(teacher_code)
    
    async def get_by_auth_id(self, auth_id: str) -> Optional[Teacher]:
        """Get teacher by auth ID."""
        return await self.repository.get_by_auth_id(auth_id)
    
    async def get_by_faculty(self, faculty_id: int) -> List[Teacher]:
        """Get teachers by faculty."""
        return await self.repository.get_by_faculty(faculty_id)
    
    async def get_by_department(self, department_id: int) -> List[Teacher]:
        """Get teachers by department."""
        return await self.repository.get_by_department(department_id)
    
    async def search_by_name(self, name: str) -> List[Teacher]:
        """Search teachers by name."""
        return await self.repository.search_by_name(name)
    
    async def create(self, data: Dict[str, Any]) -> Optional[Teacher]:
        """Create teacher with validation."""
        # Check if teacher code is unique
        existing = await self.repository.get_by_teacher_code(data.get("teacher_code"))
        if existing:
            raise ValueError("Teacher code already exists")
        
        return await self.repository.create(data)
