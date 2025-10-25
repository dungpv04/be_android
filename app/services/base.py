from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, TypeVar, Generic
from supabase import Client
from app.repositories.base import BaseRepository

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """Base service class with common business logic operations."""
    
    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository
    
    async def create(self, data: Dict[str, Any]) -> Optional[T]:
        """Create a new record with business logic validation."""
        # Override in subclasses for specific validation
        return await self.repository.create(data)
    
    async def get_by_id(self, record_id: int) -> Optional[T]:
        """Get a record by ID."""
        return await self.repository.get_by_id(record_id)
    
    async def get_all(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get all records with pagination."""
        return await self.repository.get_all(page, limit)
    
    async def update(self, record_id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update a record with business logic validation."""
        # Check if record exists
        existing = await self.repository.get_by_id(record_id)
        if not existing:
            return None
        
        # Override in subclasses for specific validation
        return await self.repository.update(record_id, data)
    
    async def delete(self, record_id: int) -> bool:
        """Delete a record with business logic validation."""
        # Check if record exists
        existing = await self.repository.get_by_id(record_id)
        if not existing:
            return False
        
        # Override in subclasses for specific validation (e.g., check dependencies)
        return await self.repository.delete(record_id)
    
    async def exists(self, record_id: int) -> bool:
        """Check if a record exists."""
        return await self.repository.exists(record_id)
