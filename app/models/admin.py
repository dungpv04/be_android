"""
Admin model for ORM operations.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class Admin(Base):
    """Admin model representing admin users."""
    
    __tablename__ = "admin"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    auth_id = Column(UUID(as_uuid=True), nullable=True, unique=True, index=True)
    
    def __repr__(self):
        return f"<Admin(id={self.id}, auth_id={self.auth_id})>"
