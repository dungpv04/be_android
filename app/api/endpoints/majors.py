"""
Majors API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from app.repositories.majors import MajorRepository
from app.schemas.academic import Major, MajorCreate, MajorUpdate
from app.schemas.base import PaginatedResponse


router = APIRouter(prefix="/majors", tags=["majors"])


@router.get("/", response_model=PaginatedResponse)
async def list_majors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by name or code")):
    try:
        repo = MajorRepository()
        if search:
            # Simple client-side filter since Supabase OR ilike may vary; can optimize later
            items = await repo.get_all(skip=0, limit=1000)
            filtered = [i for i in items if search.lower() in i.get("name", "").lower() or search.lower() in i.get("code", "").lower()]
            paged = filtered[skip:skip+limit]
            majors = [Major(**m) for m in paged]
            return PaginatedResponse.create(items=majors, total=len(filtered), skip=skip, limit=limit)
        else:
            items = await repo.get_all(skip=skip, limit=limit)
            majors = [Major(**m) for m in items]
            return PaginatedResponse.create(items=majors, total=len(items), skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{major_id}", response_model=Major)
async def get_major(
    major_id: int):
    try:
        repo = MajorRepository()
        data = await repo.get_by_id(major_id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Major not found")
        return Major(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=Major, status_code=status.HTTP_201_CREATED)
async def create_major(
    payload: MajorCreate):
    try:
        repo = MajorRepository()
        # Enforce unique code
        existing = await repo.get_by_code(payload.code)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Major code already exists")
        created = await repo.create(payload)
        return Major(**created)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{major_id}", response_model=Major)
async def update_major(
    major_id: int,
    payload: MajorUpdate):
    try:
        repo = MajorRepository()
        existing = await repo.get_by_id(major_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Major not found")
        updated = await repo.update(major_id, payload)
        if not updated:
            return Major(**existing)
        return Major(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{major_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_major(
    major_id: int):
    try:
        repo = MajorRepository()
        ok = await repo.delete(major_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Major not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


