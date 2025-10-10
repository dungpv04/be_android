"""
TeachingSessions API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List

from app.core.dependencies import get_current_user, get_teacher_user
from app.repositories.teaching_sessions import TeachingSessionRepository
from app.schemas.base import PaginatedResponse
from app.schemas.teaching_sessions import (
    TeachingSession,
    TeachingSessionCreate,
    TeachingSessionUpdate,
)


router = APIRouter(prefix="/sessions", tags=["teaching_sessions"])


@router.get("/", response_model=PaginatedResponse)
async def list_sessions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = TeachingSessionRepository()
        items_data = await repo.get_all(skip=skip, limit=limit)
        items = [TeachingSession(**item) for item in items_data]
        total = len(items_data)
        return PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id}", response_model=TeachingSession)
async def get_session(
    id: int,
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = TeachingSessionRepository()
        data = await repo.get_by_id(id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teaching session not found")
        return TeachingSession(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=TeachingSession, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: TeachingSessionCreate,
    teacher_user: dict = Depends(get_teacher_user),
):
    try:
        repo = TeachingSessionRepository()
        created = await repo.create(payload)
        return TeachingSession(**created)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id}", response_model=TeachingSession)
async def update_session(
    id: int,
    payload: TeachingSessionUpdate,
    teacher_user: dict = Depends(get_teacher_user),
):
    try:
        repo = TeachingSessionRepository()
        existing = await repo.get_by_id(id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teaching session not found")
        updated = await repo.update(id, payload)
        if not updated:
            return TeachingSession(**existing)
        return TeachingSession(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    id: int,
    teacher_user: dict = Depends(get_teacher_user),
):
    try:
        repo = TeachingSessionRepository()
        ok = await repo.delete(id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teaching session not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/class/{class_id}", response_model=List[TeachingSession])
async def list_by_class(
    class_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
):
    try:
        repo = TeachingSessionRepository()
        items = await repo.get_by_class(class_id, skip=skip, limit=limit)
        return [TeachingSession(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


