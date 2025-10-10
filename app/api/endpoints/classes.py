"""
Classes API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List

from app.core.dependencies import get_current_user, get_teacher_user
from app.repositories.classes import ClassRepository
from app.schemas.base import PaginatedResponse
from app.schemas.classes import Class as ClassSchema, ClassCreate, ClassUpdate


router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("/", response_model=PaginatedResponse)
async def list_classes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = ClassRepository()
        items = await repo.get_all(skip=skip, limit=limit)
        if search:
            s = search.lower()
            items = [i for i in items if s in (i.get("name", "").lower()) or s in (i.get("code", "").lower())]
        classes = [ClassSchema(**i) for i in items]
        total = len(items)
        return PaginatedResponse.create(items=classes, total=total, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{class_id}", response_model=ClassSchema)
async def get_class(
    class_id: int,
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = ClassRepository()
        data = await repo.get_by_id(class_id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
        return ClassSchema(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=ClassSchema, status_code=status.HTTP_201_CREATED)
async def create_class(
    payload: ClassCreate,
    teacher_user: dict = Depends(get_teacher_user),
):
    try:
        repo = ClassRepository()
        # unique code check
        existing = await repo.get_by_code(payload.class_code)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Class code already exists")
        created = await repo.create(payload)
        return ClassSchema(**created)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{class_id}", response_model=ClassSchema)
async def update_class(
    class_id: int,
    payload: ClassUpdate,
    teacher_user: dict = Depends(get_teacher_user),
):
    try:
        repo = ClassRepository()
        existing = await repo.get_by_id(class_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
        updated = await repo.update(class_id, payload)
        if not updated:
            return ClassSchema(**existing)
        return ClassSchema(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: int,
    teacher_user: dict = Depends(get_teacher_user),
):
    try:
        repo = ClassRepository()
        ok = await repo.delete(class_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/teacher/{teacher_id}", response_model=List[ClassSchema])
async def list_by_teacher(
    teacher_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = ClassRepository()
        items = await repo.get_by_teacher(teacher_id, skip=skip, limit=limit)
        return [ClassSchema(**i) for i in items]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


