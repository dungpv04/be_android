"""
Major repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any

from app.services.supabase import SupabaseService
from app.schemas.academic import MajorCreate, MajorUpdate


class MajorRepository:
    """Repository for majors using Supabase."""

    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "majors"

    async def create(self, data: MajorCreate) -> Dict[str, Any]:
        try:
            payload = {
                "name": data.name,
                "code": data.code,
            }
            response = self.supabase_service.client.table(self.table_name).insert(payload).execute()
            if response.data:
                return response.data[0]
            raise Exception("Failed to create major")
        except Exception as e:
            raise Exception(f"Error creating major: {str(e)}")

    async def get_by_id(self, major_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", major_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching major: {str(e)}")

    async def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("code", code).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching major by code: {str(e)}")

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            response = (
                self.supabase_service.client.table(self.table_name)
                .select("*")
                .range(skip, skip + limit - 1)
                .execute()
            )
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching majors: {str(e)}")

    async def update(self, major_id: int, data: MajorUpdate) -> Optional[Dict[str, Any]]:
        try:
            d = data.dict(exclude_unset=True)
            if not d:
                return None
            response = (
                self.supabase_service.client.table(self.table_name)
                .update(d)
                .eq("id", major_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating major: {str(e)}")

    async def delete(self, major_id: int) -> bool:
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", major_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting major: {str(e)}")

    async def exists_by_code(self, code: str) -> bool:
        try:
            response = self.supabase_service.client.table(self.table_name).select("id").eq("code", code).execute()
            return len(response.data) > 0
        except Exception:
            return False


