"""
Admin repository for Supabase operations.
"""
from typing import Optional, Dict, Any
from uuid import UUID

from app.services.supabase import SupabaseService


class AdminRepository:
    """Repository for admin operations using Supabase."""
    
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "admin"
    
    async def get_by_auth_id(self, auth_id: str) -> Optional[Dict[str, Any]]:
        """Get admin by auth ID."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("auth_id", str(auth_id)).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            return None
    
    async def get_by_id(self, admin_id: int) -> Optional[Dict[str, Any]]:
        """Get admin by ID."""
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", admin_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            return None