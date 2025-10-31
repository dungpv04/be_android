from typing import Optional, Dict, Any
from supabase import Client
from app.models import Admin
from app.repositories import AdminRepository
from app.services.base import BaseService


class AdminService(BaseService):
    """Service for Admin operations."""
    
    def __init__(self, supabase: Client):
        self.repository = AdminRepository(supabase)
    
    async def get_by_auth_id(self, auth_id: str) -> Optional[Admin]:
        """Get admin by auth ID."""
        return await self.repository.get_by_auth_id(auth_id)
    
    async def create(self, data: Dict[str, Any]) -> Optional[Admin]:
        """Create admin."""
        return await self.repository.create(data)
