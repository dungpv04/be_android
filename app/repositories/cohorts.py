"""
Cohort repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any

from app.services.supabase import SupabaseService
from app.schemas.academic import CohortCreate, CohortUpdate


class CohortRepository:
    """Repository for cohorts using Supabase."""

    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "cohorts"

    async def create(self, data: CohortCreate) -> Dict[str, Any]:
        try:
            payload = {
                "name": data.name,
                "start_year": data.start_year,
            }
            response = self.supabase_service.client.table(self.table_name).insert(payload).execute()
            if response.data:
                return response.data[0]
            raise Exception("Failed to create cohort")
        except Exception as e:
            raise Exception(f"Error creating cohort: {str(e)}")

    async def get_by_id(self, cohort_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", cohort_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching cohort: {str(e)}")

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
            raise Exception(f"Error fetching cohorts: {str(e)}")

    async def update(self, cohort_id: int, data: CohortUpdate) -> Optional[Dict[str, Any]]:
        try:
            d = data.dict(exclude_unset=True)
            if not d:
                return None
            response = (
                self.supabase_service.client.table(self.table_name)
                .update(d)
                .eq("id", cohort_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating cohort: {str(e)}")

    async def delete(self, cohort_id: int) -> bool:
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", cohort_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting cohort: {str(e)}")


