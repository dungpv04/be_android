"""
Base repository pattern for data access operations.
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime

from app.core.database import get_db

# Type variables for generic repository
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and optional filters."""
        query = db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        if hasattr(obj_in, 'dict'):
            obj_data = obj_in.dict()
        else:
            obj_data = obj_in.__dict__
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        if hasattr(obj_in, 'dict'):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in.__dict__
        
        # Add updated_at timestamp if model has it
        if hasattr(db_obj, 'updated_at'):
            update_data['updated_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        """Delete a record by ID."""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        query = db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    def exists(self, db: Session, id: int) -> bool:
        """Check if record exists by ID."""
        return db.query(self.model).filter(self.model.id == id).first() is not None


class RepositoryMixin:
    """Mixin class for common repository operations."""
    
    def get_by_field(
        self, 
        db: Session, 
        field_name: str, 
        field_value: Any
    ) -> Optional[ModelType]:
        """Get record by specific field."""
        if hasattr(self.model, field_name):
            return db.query(self.model).filter(
                getattr(self.model, field_name) == field_value
            ).first()
        return None
    
    def get_multi_by_field(
        self, 
        db: Session, 
        field_name: str, 
        field_value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records by specific field."""
        if hasattr(self.model, field_name):
            return db.query(self.model).filter(
                getattr(self.model, field_name) == field_value
            ).offset(skip).limit(limit).all()
        return []
    
    def bulk_create(self, db: Session, objects_data: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records in bulk."""
        db_objects = [self.model(**obj_data) for obj_data in objects_data]
        db.add_all(db_objects)
        db.commit()
        for obj in db_objects:
            db.refresh(obj)
        return db_objects
    
    def soft_delete(self, db: Session, id: int) -> Optional[ModelType]:
        """Soft delete a record (if model supports it)."""
        obj = db.query(self.model).get(id)
        if obj and hasattr(obj, 'is_deleted'):
            obj.is_deleted = True
            if hasattr(obj, 'deleted_at'):
                obj.deleted_at = datetime.utcnow()
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj
