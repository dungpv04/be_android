"""
Schemas for face_templates table aligned with DB columns.
"""
from typing import Optional, Dict, Any
from pydantic import Field

from app.schemas.base import (
    BaseSchema,
    CreateSchemaBase,
    UpdateSchemaBase,
    ResponseSchemaBase,
    TimestampSchema,
)


class FaceTemplateBase(BaseSchema):
    """Base schema mapping to face_templates columns."""

    student_id: int = Field(..., description="Student ID")
    image_path: str = Field(..., description="Path to face image in storage")
    face_encoding: Dict[str, Any] = Field(..., description="Face encoding JSON payload")
    is_primary: bool = Field(default=False, description="Whether this is the primary face template")


class FaceTemplateCreate(FaceTemplateBase, CreateSchemaBase):
    """Create face template payload."""
    pass


class FaceTemplateUpdate(UpdateSchemaBase):
    """Update face template payload."""

    image_path: Optional[str] = None
    face_encoding: Optional[Dict[str, Any]] = None
    is_primary: Optional[bool] = None


class FaceTemplate(FaceTemplateBase, ResponseSchemaBase, TimestampSchema):
    """Face template response schema."""
    pass


