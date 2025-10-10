"""
FaceTemplate repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any

from app.services.supabase import SupabaseService
from app.schemas.face_templates import FaceTemplateCreate, FaceTemplateUpdate


class FaceTemplateRepository:
    """Repository for face_templates using Supabase."""

    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "face_templates"

    async def create(self, data: FaceTemplateCreate) -> Dict[str, Any]:
        try:
            payload = {
                "student_id": data.student_id,
                "image_path": data.image_path,
                "face_encoding": data.face_encoding,
                "is_primary": data.is_primary,
            }
            response = self.supabase_service.client.table(self.table_name).insert(payload).execute()
            if response.data:
                return response.data[0]
            raise Exception("Failed to create face template")
        except Exception as e:
            raise Exception(f"Error creating face template: {str(e)}")

    async def get_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", template_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching face template: {str(e)}")

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
            raise Exception(f"Error fetching face templates: {str(e)}")

    async def get_by_student(self, student_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            response = (
                self.supabase_service.client.table(self.table_name)
                .select("*")
                .eq("student_id", student_id)
                .range(skip, skip + limit - 1)
                .execute()
            )
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching face templates by student: {str(e)}")

    async def update(self, template_id: int, data: FaceTemplateUpdate) -> Optional[Dict[str, Any]]:
        try:
            d = data.dict(exclude_unset=True)
            if not d:
                return None
            response = (
                self.supabase_service.client.table(self.table_name)
                .update(d)
                .eq("id", template_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating face template: {str(e)}")

    async def delete(self, template_id: int) -> bool:
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", template_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting face template: {str(e)}")


