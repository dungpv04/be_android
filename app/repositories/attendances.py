"""
Attendance repository for Supabase operations.
"""
from typing import Optional, List, Dict, Any

from app.services.supabase import SupabaseService
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate


class AttendanceRepository:
    """Repository for attendances using Supabase."""

    def __init__(self):
        self.supabase_service = SupabaseService()
        self.table_name = "attendances"

    async def create(self, data: AttendanceCreate) -> Dict[str, Any]:
        try:
            payload: Dict[str, Any] = {
                "session_id": data.session_id,
                "student_id": data.student_id,
                "status": data.status.value if hasattr(data.status, "value") else data.status,
            }
            if data.check_in_time is not None:
                payload["attendance_time"] = data.check_in_time.isoformat()
            if data.location is not None:
                payload["location"] = data.location
            if data.notes is not None:
                payload["notes"] = data.notes
            if data.is_late is not None:
                payload["is_late"] = data.is_late
            if data.late_minutes is not None:
                payload["late_minutes"] = data.late_minutes

            response = self.supabase_service.client.table(self.table_name).insert(payload).execute()
            if response.data:
                return response.data[0]
            raise Exception("Failed to create attendance")
        except Exception as e:
            raise Exception(f"Error creating attendance: {str(e)}")

    async def get_by_id(self, att_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.supabase_service.client.table(self.table_name).select("*").eq("id", att_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching attendance: {str(e)}")

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
            raise Exception(f"Error fetching attendances: {str(e)}")

    async def get_by_session(self, session_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            response = (
                self.supabase_service.client.table(self.table_name)
                .select("*")
                .eq("session_id", session_id)
                .range(skip, skip + limit - 1)
                .execute()
            )
            return response.data or []
        except Exception as e:
            raise Exception(f"Error fetching by session: {str(e)}")

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
            raise Exception(f"Error fetching by student: {str(e)}")

    async def update(self, att_id: int, data: AttendanceUpdate) -> Optional[Dict[str, Any]]:
        try:
            d = data.dict(exclude_unset=True)
            update_data: Dict[str, Any] = {}
            if "status" in d and d["status"] is not None:
                update_data["status"] = d["status"].value if hasattr(d["status"], "value") else d["status"]
            if "check_in_time" in d and d["check_in_time"] is not None:
                update_data["attendance_time"] = d["check_in_time"].isoformat()
            if "check_out_time" in d and d["check_out_time"] is not None:
                update_data["check_out_time"] = d["check_out_time"].isoformat()
            if "method" in d and d["method"] is not None:
                update_data["method"] = d["method"].value if hasattr(d["method"], "value") else d["method"]
            if "location" in d and d["location"] is not None:
                update_data["location"] = d["location"]
            if "notes" in d and d["notes"] is not None:
                update_data["notes"] = d["notes"]
            if "is_late" in d and d["is_late"] is not None:
                update_data["is_late"] = d["is_late"]
            if "late_minutes" in d and d["late_minutes"] is not None:
                update_data["late_minutes"] = d["late_minutes"]

            if not update_data:
                return None

            response = (
                self.supabase_service.client.table(self.table_name)
                .update(update_data)
                .eq("id", att_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error updating attendance: {str(e)}")

    async def delete(self, att_id: int) -> bool:
        try:
            response = self.supabase_service.client.table(self.table_name).delete().eq("id", att_id).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Error deleting attendance: {str(e)}")


