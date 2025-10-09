"""
Student repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date

from app.services.supabase import SupabaseService
from app.schemas.users import StudentCreate, StudentUpdate, Student


class StudentRepository:
    """Repository for student operations using Supabase."""
    
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "students"
    
    async def create(self, student_data: StudentCreate) -> Dict[str, Any]:
        """Create a new student record."""
        try:
            # Convert UUID to string for Supabase
            data = {
                "student_code": student_data.student_code,
                "full_name": student_data.full_name,
                "phone": student_data.phone,
                "birth_date": student_data.birth_date.isoformat() if student_data.birth_date else None,
                "auth_id": str(student_data.auth_id),
                "major_id": student_data.major_id,
                "cohort_id": student_data.cohort_id,
                "class_id": student_data.class_id
            }
            
            response = self.supabase_service.client.table(self.table_name).insert(data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to create student record")
                
        except Exception as e:
            raise Exception(f"Error creating student: {str(e)}")
    
    async def get_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Get student by ID."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching student: {str(e)}")
    
    async def get_by_student_code(self, student_code: str) -> Optional[Dict[str, Any]]:
        """Get student by student code."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("student_code", student_code).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching student by code: {str(e)}")
    
    async def get_by_auth_id(self, auth_id: UUID) -> Optional[Dict[str, Any]]:
        """Get student by auth ID."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("auth_id", str(auth_id)).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching student by auth ID: {str(e)}")
    
    async def get_by_major(self, major_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get students by major."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("major_id", major_id).range(skip, skip + limit - 1).execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching students by major: {str(e)}")
    
    async def get_by_cohort(self, cohort_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get students by cohort."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("cohort_id", cohort_id).range(skip, skip + limit - 1).execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching students by cohort: {str(e)}")
    
    async def get_by_class(self, class_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get students by class."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("class_id", class_id).range(skip, skip + limit - 1).execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching students by class: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all students with pagination."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").range(skip, skip + limit - 1).execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching students: {str(e)}")
    
    async def update(self, student_id: int, student_data: StudentUpdate) -> Optional[Dict[str, Any]]:
        """Update student record."""
        try:
            # Only include non-None values
            update_data = {}
            for field, value in student_data.dict(exclude_unset=True).items():
                if value is not None:
                    if field == "birth_date" and isinstance(value, date):
                        update_data[field] = value.isoformat()
                    else:
                        update_data[field] = value
            
            if not update_data:
                return None
            
            response = self.supabase_service.client.table(self.table_name).update(update_data).eq("id", student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating student: {str(e)}")
    
    async def delete(self, student_id: int) -> bool:
        """Delete student record."""
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", student_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting student: {str(e)}")
    
    async def exists_by_student_code(self, student_code: str) -> bool:
        """Check if student code already exists."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("id").eq("student_code", student_code).execute()
            return len(response.data) > 0
        except Exception as e:
            return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count total students with optional filters."""
        try:
            query = self.supabase_service.client.table(self.table_name).select("id", count="exact")
            
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)
            
            response = query.execute()
            return response.count or 0
        except Exception as e:
            return 0
