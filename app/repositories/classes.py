"""
Class repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any

from app.services.supabase import SupabaseService
from app.schemas.classes import ClassCreate, ClassUpdate


class ClassRepository:
    """Repository for classes using Supabase."""

    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "classes"

    async def create(self, data: ClassCreate) -> Dict[str, Any]:
        """Create a new class mapping schema fields to DB columns."""
        try:
            payload = {
                # Map schema fields to DB columns
                "name": data.class_name,
                "code": data.class_code,
                "subject_id": data.subject_id,
                "teacher_id": data.teacher_id,
                "status": data.status.value if hasattr(data.status, "value") else data.status,
            }
            response = self.supabase_service.client.table(self.table_name).insert(payload).execute()
            if response.data:
                return response.data[0]
            raise Exception("Failed to create class")
        except Exception as e:
            raise Exception(f"Error creating class: {str(e)}")

    async def get_by_id(self, class_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", class_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching class: {str(e)}")

    async def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("code", code).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching class by code: {str(e)}")

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
            raise Exception(f"Error fetching classes: {str(e)}")

    async def get_by_teacher(self, teacher_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            response = (
                self.supabase_service.client.table(self.table_name)
                .select("*")
                .eq("teacher_id", teacher_id)
                .range(skip, skip + limit - 1)
                .execute()
            )
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching classes by teacher: {str(e)}")

    async def update(self, class_id: int, data: ClassUpdate) -> Optional[Dict[str, Any]]:
        try:
            update_data: Dict[str, Any] = {}
            d = data.dict(exclude_unset=True)
            if "class_name" in d and d["class_name"] is not None:
                update_data["name"] = d["class_name"]
            if "class_code" in d and d["class_code"] is not None:
                update_data["code"] = d["class_code"]
            if "subject_id" in d and d["subject_id"] is not None:
                update_data["subject_id"] = d["subject_id"]
            if "teacher_id" in d and d["teacher_id"] is not None:
                update_data["teacher_id"] = d["teacher_id"]
            if "status" in d and d["status"] is not None:
                status_val = d["status"].value if hasattr(d["status"], "value") else d["status"]
                update_data["status"] = status_val

            if not update_data:
                return None

            response = (
                self.supabase_service.client.table(self.table_name)
                .update(update_data)
                .eq("id", class_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating class: {str(e)}")

    async def delete(self, class_id: int) -> bool:
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", class_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting class: {str(e)}")


