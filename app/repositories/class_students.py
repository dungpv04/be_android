"""
ClassStudent repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any

from app.services.supabase import SupabaseService
from app.schemas.classes import ClassStudentCreate, ClassStudentUpdate


class ClassStudentRepository:
    """Repository for class_students operations using Supabase."""

    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "class_students"

    async def create(self, data: ClassStudentCreate) -> Dict[str, Any]:
        """Create a new class_students record."""
        try:
            payload = {
                "class_id": data.class_id,
                "student_id": data.student_id,
                # Map schema fields to DB columns when present in table
                # status defaults to 'active' in DB; honor is_active if provided
                "status": "active" if getattr(data, "is_active", True) else "dropped",
            }

            # Optional fields if your table has them; ignore if not present
            if getattr(data, "enrollment_date", None) is not None:
                payload["enrolled_at"] = data.enrollment_date.isoformat()

            if getattr(data, "notes", None) is not None:
                payload["notes"] = data.notes

            response = self.supabase_service.client.table(self.table_name).insert(payload).execute()
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to create class_students record")
        except Exception as e:
            raise Exception(f"Error creating class_students: {str(e)}")

    async def get_by_id(self, cs_id: int) -> Optional[Dict[str, Any]]:
        """Get class_students by ID."""
        try:
            response = (
                self.supabase_service.client.table(self.table_name)
                .select("*")
                .eq("id", cs_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching class_students: {str(e)}")

    async def get_all(
        self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get class_students list with optional filters and pagination."""
        try:
            query = self.supabase_service.client.table(self.table_name).select("*")

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            response = query.range(skip, skip + limit - 1).execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching class_students: {str(e)}")

    async def get_by_class(self, class_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get enrollments by class_id."""
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
            raise Exception(f"Error fetching by class_id: {str(e)}")

    async def get_by_student(self, student_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get enrollments by student_id."""
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
            raise Exception(f"Error fetching by student_id: {str(e)}")

    async def update(self, cs_id: int, data: ClassStudentUpdate) -> Optional[Dict[str, Any]]:
        """Update class_students record."""
        try:
            update_data: Dict[str, Any] = {}

            d = data.dict(exclude_unset=True)
            if "enrollment_date" in d and d["enrollment_date"] is not None:
                update_data["enrolled_at"] = d["enrollment_date"].isoformat()

            if "is_active" in d and d["is_active"] is not None:
                update_data["status"] = "active" if d["is_active"] else "dropped"

            if "notes" in d and d["notes"] is not None:
                update_data["notes"] = d["notes"]

            if not update_data:
                return None

            response = (
                self.supabase_service.client.table(self.table_name)
                .update(update_data)
                .eq("id", cs_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating class_students: {str(e)}")

    async def delete(self, cs_id: int) -> bool:
        """Delete class_students record."""
        try:
            response = (
                self.supabase_service.client.table(self.table_name)
                .delete()
                .eq("id", cs_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting class_students: {str(e)}")


