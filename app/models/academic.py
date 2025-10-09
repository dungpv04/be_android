"""
Academic structure models: majors, subjects, cohorts.
"""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Major(BaseModel):
    """Academic major/department model."""
    
    __tablename__ = "majors"
    
    name = Column(String, nullable=False, comment="Major name")
    code = Column(String, nullable=False, unique=True, comment="Unique major code")
    
    # Relationships
    students = relationship("Student", back_populates="major", lazy="select")
    
    def __repr__(self):
        return f"<Major(code='{self.code}', name='{self.name}')>"


class Subject(BaseModel):
    """Subject/course model."""
    
    __tablename__ = "subjects"
    
    name = Column(String, nullable=False, comment="Subject name")
    code = Column(String, nullable=False, unique=True, comment="Unique subject code")
    
    # Relationships
    classes = relationship("Class", back_populates="subject", lazy="select")
    
    def __repr__(self):
        return f"<Subject(code='{self.code}', name='{self.name}')>"


class Cohort(BaseModel):
    """Student cohort/batch model."""
    
    __tablename__ = "cohorts"
    
    name = Column(String, nullable=False, comment="Cohort name")
    start_year = Column(Integer, nullable=False, comment="Starting year")
    
    # Relationships  
    students = relationship("Student", back_populates="cohort", lazy="select")
    
    def __repr__(self):
        return f"<Cohort(name='{self.name}', year={self.start_year})>"
