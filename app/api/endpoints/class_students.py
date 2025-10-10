"""
ClassStudents API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from app.core.dependencies import get_current_user, get_teacher_user
from app.repositories.class_students import ClassStudentRepository
from app.schemas.base import PaginatedResponse
from app.schemas.classes import (
    ClassStudent,
    ClassStudentCreate,
    ClassStudentUpdate,
)


router = APIRouter(prefix="/class-students", tags=["class_students"])


@router.get("/", response_model=PaginatedResponse)
async def list_class_students(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    class_id: Optional[int] = Query(None, description="Filter by class_id"),
    student_id: Optional[int] = Query(None, description="Filter by student_id"),
    current_user: dict = Depends(get_current_user),
):
    """List enrollments with optional filters."""
    try:
        repo = ClassStudentRepository()
        filters = {}
        if class_id is not None:
            filters["class_id"] = class_id
        if student_id is not None:
            filters["student_id"] = student_id

        items_data = await repo.get_all(skip=skip, limit=limit, filters=filters or None)
        items = [ClassStudent(**item) for item in items_data]
        total = len(items_data)  # simple count; optimize later if needed
        return PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id}", response_model=ClassStudent)
async def get_class_student(
    id: int,
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = ClassStudentRepository()
        data = await repo.get_by_id(id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        return ClassStudent(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=ClassStudent, status_code=status.HTTP_201_CREATED)
async def create_class_student(
    payload: ClassStudentCreate,
    teacher_user: dict = Depends(get_teacher_user),
):
    """Create enrollment; teacher-only."""
    try:
        repo = ClassStudentRepository()
        created = await repo.create(payload)
        return ClassStudent(**created)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id}", response_model=ClassStudent)
async def update_class_student(
    id: int,
    payload: ClassStudentUpdate,
    teacher_user: dict = Depends(get_teacher_user),
):
    try:
        repo = ClassStudentRepository()
        existing = await repo.get_by_id(id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        updated = await repo.update(id, payload)
        if not updated:
            # no changes provided
            return ClassStudent(**existing)
        return ClassStudent(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class_student(
    id: int,
    teacher_user: dict = Depends(get_teacher_user),
):
    try:
        repo = ClassStudentRepository()
        ok = await repo.delete(id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/class/{class_id}", response_model=List[ClassStudent])
async def list_by_class(
    class_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = ClassStudentRepository()
        items = await repo.get_by_class(class_id, skip=skip, limit=limit)
        return [ClassStudent(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/student/{student_id}", response_model=List[ClassStudent])
async def list_by_student(
    student_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = ClassStudentRepository()
        items = await repo.get_by_student(student_id, skip=skip, limit=limit)
        return [ClassStudent(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


