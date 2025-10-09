"""
Teacher repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date

from app.services.supabase import SupabaseService
from app.schemas.users import TeacherCreate, TeacherUpdate, Teacher


class TeacherRepository:
    """Repository for teacher operations using Supabase."""
    
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "teachers"
    
    async def create(self, teacher_data: TeacherCreate) -> Dict[str, Any]:
        """Create a new teacher record."""
        try:
            # Convert UUID to string for Supabase
            data = {
                "teacher_code": teacher_data.teacher_code,
                "full_name": teacher_data.full_name,
                "phone": teacher_data.phone,
                "birth_date": teacher_data.birth_date.isoformat() if teacher_data.birth_date else None,
                "auth_id": str(teacher_data.auth_id)
            }
            
            response = self.supabase_service.client.table(self.table_name).insert(data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to create teacher record")
                
        except Exception as e:
            raise Exception(f"Error creating teacher: {str(e)}")
    
    async def get_by_id(self, teacher_id: int) -> Optional[Dict[str, Any]]:
        """Get teacher by ID."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", teacher_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching teacher: {str(e)}")
    
    async def get_by_teacher_code(self, teacher_code: str) -> Optional[Dict[str, Any]]:
        """Get teacher by teacher code."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("teacher_code", teacher_code).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching teacher by code: {str(e)}")
    
    async def get_by_auth_id(self, auth_id: UUID) -> Optional[Dict[str, Any]]:
        """Get teacher by auth ID."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("auth_id", str(auth_id)).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching teacher by auth ID: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all teachers with pagination."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").range(skip, skip + limit - 1).execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching teachers: {str(e)}")
    
    async def update(self, teacher_id: int, teacher_data: TeacherUpdate) -> Optional[Dict[str, Any]]:
        """Update teacher record."""
        try:
            # Only include non-None values
            update_data = {}
            for field, value in teacher_data.dict(exclude_unset=True).items():
                if value is not None:
                    if field == "birth_date" and isinstance(value, date):
                        update_data[field] = value.isoformat()
                    else:
                        update_data[field] = value
            
            if not update_data:
                return None
            
            response = self.supabase_service.client.table(self.table_name).update(update_data).eq("id", teacher_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating teacher: {str(e)}")
    
    async def delete(self, teacher_id: int) -> bool:
        """Delete teacher record."""
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", teacher_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting teacher: {str(e)}")
    
    async def exists_by_teacher_code(self, teacher_code: str) -> bool:
        """Check if teacher code already exists."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("id").eq("teacher_code", teacher_code).execute()
            return len(response.data) > 0
        except Exception as e:
            return False
    
    async def count(self) -> int:
        """Count total teachers."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("id", count="exact").execute()
            return response.count or 0
        except Exception as e:
            return 0
