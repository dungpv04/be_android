"""
Subject API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from app.repositories.subjects import SubjectRepository
from app.schemas.academic import Subject, SubjectCreate, SubjectUpdate
from app.schemas.base import PaginatedResponse

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("/", response_model=PaginatedResponse)
async def list_subjects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by name or code")):
    """Get all subjects with pagination and optional search."""
    try:
        subject_repo = SubjectRepository()
        
        if search:
            subjects_data = await subject_repo.search(search, skip, limit)
            total = len(subjects_data)  # Simple count for search
        else:
            subjects_data = await subject_repo.get_all(skip, limit)
            total = await subject_repo.count()
        
        # Convert to Subject schema
        subjects = [Subject(**subject) for subject in subjects_data]
        
        return PaginatedResponse.create(
            items=subjects,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subjects: {str(e)}"
        )


@router.get("/{subject_id}", response_model=Subject)
async def get_subject(
    subject_id: int):
    """Get a specific subject by ID."""
    try:
        subject_repo = SubjectRepository()
        subject_data = await subject_repo.get_by_id(subject_id)
        
        if not subject_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        return Subject(**subject_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subject: {str(e)}"
        )


@router.get("/code/{code}", response_model=Subject)
async def get_subject_by_code(
    code: str):
    """Get a subject by its code."""
    try:
        subject_repo = SubjectRepository()
        subject_data = await subject_repo.get_by_code(code.upper())
        
        if not subject_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with code '{code}' not found"
            )
        
        return Subject(**subject_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subject: {str(e)}"
        )


@router.post("/", response_model=Subject, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate):
    """Create a new subject."""
    try:
        subject_repo = SubjectRepository()
        
        # Check if code already exists
        if await subject_repo.exists_by_code(subject_data.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subject with code '{subject_data.code}' already exists"
            )
        
        created_subject = await subject_repo.create(subject_data)
        return Subject(**created_subject)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subject: {str(e)}"
        )


@router.put("/{subject_id}", response_model=Subject)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate):
    """Update a subject."""
    try:
        subject_repo = SubjectRepository()
        
        # Check if subject exists
        existing_subject = await subject_repo.get_by_id(subject_id)
        if not existing_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Check if new code conflicts with existing subjects
        if subject_data.code and subject_data.code != existing_subject['code']:
            if await subject_repo.exists_by_code(subject_data.code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subject with code '{subject_data.code}' already exists"
                )
        
        updated_subject = await subject_repo.update(subject_id, subject_data)
        if not updated_subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made to subject"
            )
        
        return Subject(**updated_subject)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subject: {str(e)}"
        )


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int):
    """Delete a subject."""
    try:
        subject_repo = SubjectRepository()
        
        # Check if subject exists
        existing_subject = await subject_repo.get_by_id(subject_id)
        if not existing_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        success = await subject_repo.delete(subject_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete subject"
            )
        
        return {"message": "Subject deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subject: {str(e)}"
        )


@router.get("/search/", response_model=List[Subject])
async def search_subjects(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results")):
    """Search subjects by name or code."""
    try:
        subject_repo = SubjectRepository()
        subjects_data = await subject_repo.search(q, 0, limit)
        
        return [Subject(**subject) for subject in subjects_data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )