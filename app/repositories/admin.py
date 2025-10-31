from typing import Optional
from supabase import Client
from app.models import Admin
from app.repositories.base import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    """Repository for Admin operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "admins", Admin)
    
    async def get_by_auth_id(self, auth_id: str) -> Optional[Admin]:
        """Get admin by auth ID."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("auth_id", auth_id).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting admin by auth ID: {e}")
            return None
