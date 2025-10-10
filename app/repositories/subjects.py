"""
Subject repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any

from app.services.supabase import SupabaseService
from app.schemas.academic import SubjectCreate, SubjectUpdate


class SubjectRepository:
    """Repository for subject operations using Supabase."""
    
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "subjects"
    
    async def create(self, subject_data: SubjectCreate) -> Dict[str, Any]:
        """Create a new subject record."""
        try:
            data = {
                "name": subject_data.name,
                "code": subject_data.code
            }
            
            response = self.supabase_service.client.table(self.table_name).insert(data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to create subject record")
                
        except Exception as e:
            raise Exception(f"Error creating subject: {str(e)}")
    
    async def get_by_id(self, subject_id: int) -> Optional[Dict[str, Any]]:
        """Get subject by ID."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", subject_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching subject: {str(e)}")
    
    async def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get subject by code."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("code", code).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching subject by code: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all subjects with pagination."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").range(skip, skip + limit - 1).execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching subjects: {str(e)}")
    
    async def update(self, subject_id: int, subject_data: SubjectUpdate) -> Optional[Dict[str, Any]]:
        """Update subject record."""
        try:
            # Only include non-None values
            update_data = {}
            for field, value in subject_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_data[field] = value
            
            if not update_data:
                return None
            
            response = self.supabase_service.client.table(self.table_name).update(update_data).eq("id", subject_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating subject: {str(e)}")
    
    async def delete(self, subject_id: int) -> bool:
        """Delete subject record."""
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", subject_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting subject: {str(e)}")
    
    async def exists_by_code(self, code: str) -> bool:
        """Check if subject code already exists."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("id").eq("code", code).execute()
            return len(response.data) > 0
        except Exception as e:
            return False
    
    async def count(self) -> int:
        """Count total subjects."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("id", count="exact").execute()
            return response.count or 0
        except Exception as e:
            return 0
    
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search subjects by name or code."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").or_(
                f"name.ilike.%{query}%,code.ilike.%{query}%"
            ).range(skip, skip + limit - 1).execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error searching subjects: {str(e)}")