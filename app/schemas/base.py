"""
Base Pydantic schemas with common functionality.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        use_enum_values=True
    )


class TimestampSchema(BaseSchema):
    """Schema mixin for timestamp fields."""
    
    created_at: datetime
    updated_at: datetime


class CreateSchemaBase(BaseSchema):
    """Base schema for create operations."""
    pass


class UpdateSchemaBase(BaseSchema):
    """Base schema for update operations."""
    pass


class ResponseSchemaBase(BaseSchema):
    """Base schema for API responses."""
    
    id: int


class PaginationParams(BaseSchema):
    """Schema for pagination parameters."""
    
    skip: int = 0
    limit: int = 100
    
    def __init__(self, skip: int = 0, limit: int = 100):
        super().__init__(skip=max(0, skip), limit=min(max(1, limit), 1000))


class PaginatedResponse(BaseSchema):
    """Generic paginated response schema."""
    
    items: list[Any]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls, 
        items: list[Any], 
        total: int, 
        skip: int, 
        limit: int
    ) -> "PaginatedResponse":
        """Create paginated response."""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total,
            has_prev=skip > 0
        )


class SuccessResponse(BaseSchema):
    """Standard success response."""
    
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseSchema):
    """Standard error response."""
    
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
