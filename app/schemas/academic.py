"""
Academic structure schemas: majors, subjects, cohorts.
"""
from typing import Optional, List
from pydantic import Field, validator

from app.schemas.base import (
    BaseSchema, 
    CreateSchemaBase, 
    UpdateSchemaBase, 
    ResponseSchemaBase, 
    TimestampSchema
)


# Major schemas
class MajorBase(BaseSchema):
    """Base major schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Major name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique major code")
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isalnum():
            raise ValueError('Code must be alphanumeric')
        return v.upper()


class MajorCreate(MajorBase, CreateSchemaBase):
    """Schema for creating a major."""
    pass


class MajorUpdate(UpdateSchemaBase):
    """Schema for updating a major."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    
    @validator('code')
    def validate_code(cls, v):
        if v is not None and not v.isalnum():
            raise ValueError('Code must be alphanumeric')
        return v.upper() if v else None


class Major(MajorBase, ResponseSchemaBase, TimestampSchema):
    """Major response schema."""
    
    students_count: Optional[int] = Field(None, description="Number of students in this major")


# Subject schemas
class SubjectBase(BaseSchema):
    """Base subject schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Subject name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique subject code")
    
    @validator('code')
    def validate_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Code must be alphanumeric (with optional - or _)')
        return v.upper()


class SubjectCreate(SubjectBase, CreateSchemaBase):
    """Schema for creating a subject."""
    pass


class SubjectUpdate(UpdateSchemaBase):
    """Schema for updating a subject."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    
    @validator('code')
    def validate_code(cls, v):
        if v is not None and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Code must be alphanumeric (with optional - or _)')
        return v.upper() if v else None


class Subject(SubjectBase, ResponseSchemaBase, TimestampSchema):
    """Subject response schema."""
    
    classes_count: Optional[int] = Field(None, description="Number of classes for this subject")


# Cohort schemas
class CohortBase(BaseSchema):
    """Base cohort schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Cohort name")
    start_year: int = Field(..., ge=2000, le=2100, description="Starting year")
    
    @validator('start_year')
    def validate_start_year(cls, v):
        from datetime import datetime
        current_year = datetime.now().year
        if v > current_year + 5:
            raise ValueError('Start year cannot be more than 5 years in the future')
        return v


class CohortCreate(CohortBase, CreateSchemaBase):
    """Schema for creating a cohort."""
    pass


class CohortUpdate(UpdateSchemaBase):
    """Schema for updating a cohort."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_year: Optional[int] = Field(None, ge=2000, le=2100)
    
    @validator('start_year')
    def validate_start_year(cls, v):
        if v is not None:
            from datetime import datetime
            current_year = datetime.now().year
            if v > current_year + 5:
                raise ValueError('Start year cannot be more than 5 years in the future')
        return v


class Cohort(CohortBase, ResponseSchemaBase):
    """Cohort response schema."""
    
    students_count: Optional[int] = Field(None, description="Number of students in this cohort")
