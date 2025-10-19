"""
FaceTemplates API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List

from app.repositories.face_templates import FaceTemplateRepository
from app.schemas.base import PaginatedResponse
from app.schemas.face_templates import (
    FaceTemplate,
    FaceTemplateCreate,
    FaceTemplateUpdate,
)


router = APIRouter(prefix="/face-templates", tags=["face_templates"])


@router.get("/", response_model=PaginatedResponse)
async def list_face_templates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")):
    try:
        repo = FaceTemplateRepository()
        items_data = await repo.get_all(skip=skip, limit=limit)
        items = [FaceTemplate(**item) for item in items_data]
        total = len(items_data)
        return PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id}", response_model=FaceTemplate)
async def get_face_template(
    id: int):
    try:
        repo = FaceTemplateRepository()
        data = await repo.get_by_id(id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Face template not found")
        return FaceTemplate(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=FaceTemplate, status_code=status.HTTP_201_CREATED)
async def create_face_template(
    payload: FaceTemplateCreate):
    try:
        repo = FaceTemplateRepository()
        created = await repo.create(payload)
        return FaceTemplate(**created)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id}", response_model=FaceTemplate)
async def update_face_template(
    id: int,
    payload: FaceTemplateUpdate):
    try:
        repo = FaceTemplateRepository()
        existing = await repo.get_by_id(id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Face template not found")
        updated = await repo.update(id, payload)
        if not updated:
            return FaceTemplate(**existing)
        return FaceTemplate(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_face_template(
    id: int):
    try:
        repo = FaceTemplateRepository()
        ok = await repo.delete(id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Face template not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/student/{student_id}", response_model=List[FaceTemplate])
async def list_by_student(
    student_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)):
    try:
        repo = FaceTemplateRepository()
        items = await repo.get_by_student(student_id, skip=skip, limit=limit)
        return [FaceTemplate(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


