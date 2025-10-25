from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, TypeVar, Generic, Type
from supabase import Client
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseRepository(ABC, Generic[T]):
    """Base repository class with common CRUD operations."""
    
    def __init__(self, supabase: Client, table_name: str, model_class: Type[T]):
        self.supabase = supabase
        self.table_name = table_name
        self.model_class = model_class
    
    async def create(self, data: Dict[str, Any]) -> Optional[T]:
        """Create a new record."""
        try:
            # Convert date/datetime objects to ISO format strings
            serialized_data = self._serialize_data(data)
            print(f"Creating record in {self.table_name} with serialized data: {serialized_data}")
            
            response = self.supabase.table(self.table_name).insert(serialized_data).execute()
            print(f"Supabase response: {response}")
            
            if response.data:
                print(f"Successfully created record: {response.data[0]}")
                return self.model_class(**response.data[0])
            else:
                print(f"No data returned from insert operation")
                return None
        except Exception as e:
            print(f"Error creating {self.table_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _serialize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize data to be JSON compatible."""
        from datetime import date, datetime, time
        
        serialized = {}
        for key, value in data.items():
            if isinstance(value, date):
                serialized[key] = value.isoformat()
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, time):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value
        
        return serialized
    
    async def get_by_id(self, record_id: int) -> Optional[T]:
        """Get a record by ID."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("id", record_id).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting {self.table_name} by ID: {e}")
            return None
    
    async def get_all(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get all records with pagination."""
        try:
            offset = (page - 1) * limit
            
            # Get total count
            count_response = self.supabase.table(self.table_name).select("*", count="exact").execute()
            total = count_response.count if count_response.count else 0
            
            # Get paginated data
            response = self.supabase.table(self.table_name).select("*").range(offset, offset + limit - 1).execute()
            
            items = [self.model_class(**item) for item in response.data] if response.data else []
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
        except Exception as e:
            print(f"Error getting all {self.table_name}: {e}")
            return {"items": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}
    
    async def update(self, record_id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID."""
        try:
            # Remove None values and serialize data
            update_data = {k: v for k, v in data.items() if v is not None}
            if not update_data:
                return await self.get_by_id(record_id)
            
            serialized_data = self._serialize_data(update_data)
            response = self.supabase.table(self.table_name).update(serialized_data).eq("id", record_id).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error updating {self.table_name}: {e}")
            return None
    
    async def delete(self, record_id: int) -> bool:
        """Delete a record by ID."""
        try:
            response = self.supabase.table(self.table_name).delete().eq("id", record_id).execute()
            return response.data is not None
        except Exception as e:
            print(f"Error deleting {self.table_name}: {e}")
            return False
    
    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """Find records by a specific field value."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq(field, value).execute()
            return [self.model_class(**item) for item in response.data] if response.data else []
        except Exception as e:
            print(f"Error finding {self.table_name} by {field}: {e}")
            return []
    
    async def exists(self, record_id: int) -> bool:
        """Check if a record exists by ID."""
        try:
            response = self.supabase.table(self.table_name).select("id").eq("id", record_id).execute()
            return len(response.data) > 0 if response.data else False
        except Exception as e:
            print(f"Error checking if {self.table_name} exists: {e}")
            return False
