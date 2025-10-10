"""
TeachingSession repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any

from app.services.supabase import SupabaseService
from app.schemas.teaching_sessions import TeachingSessionCreate, TeachingSessionUpdate


class TeachingSessionRepository:
    """Repository for teaching_sessions using Supabase."""

    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "teaching_sessions"

    async def create(self, data: TeachingSessionCreate) -> Dict[str, Any]:
        try:
            payload = data.dict()
            response = self.supabase_service.client.table(self.table_name).insert(payload).execute()
            if response.data:
                return response.data[0]
            raise Exception("Failed to create teaching session")
        except Exception as e:
            raise Exception(f"Error creating teaching session: {str(e)}")

    async def get_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching teaching session: {str(e)}")

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
            raise Exception(f"Error fetching teaching sessions: {str(e)}")

    async def get_by_class(self, class_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            response = (
                self.supabase_service.client.table(self.table_name)
                .select("*")
                .eq("class_id", class_id)
                .range(skip, skip + limit - 1)
                .execute()
            )
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching sessions by class: {str(e)}")

    async def update(self, session_id: int, data: TeachingSessionUpdate) -> Optional[Dict[str, Any]]:
        try:
            d = data.dict(exclude_unset=True)
            if not d:
                return None
            response = (
                self.supabase_service.client.table(self.table_name)
                .update(d)
                .eq("id", session_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating teaching session: {str(e)}")

    async def delete(self, session_id: int) -> bool:
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", session_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting teaching session: {str(e)}")


