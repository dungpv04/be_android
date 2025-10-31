from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Admin Schemas
class AdminCreate(BaseModel):
    """Schema for creating admin."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class AdminUpdate(BaseModel):
    """Schema for updating admin."""
    pass  # Admin has minimal fields, mainly just auth_id


class AdminResponse(BaseModel):
    """Schema for admin response."""
    id: int
    auth_id: str
    created_at: datetime
    updated_at: Optional[datetime]
