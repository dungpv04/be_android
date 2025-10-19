"""
Cohorts API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List

from app.repositories.cohorts import CohortRepository
from app.schemas.academic import Cohort, CohortCreate, CohortUpdate
from app.schemas.base import PaginatedResponse


router = APIRouter(prefix="/cohorts", tags=["cohorts"])


@router.get("/", response_model=PaginatedResponse)
async def list_cohorts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")):
    try:
        repo = CohortRepository()
        items = await repo.get_all(skip=skip, limit=limit)
        cohorts = [Cohort(**i) for i in items]
        return PaginatedResponse.create(items=cohorts, total=len(items), skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{cohort_id}", response_model=Cohort)
async def get_cohort(
    cohort_id: int):
    try:
        repo = CohortRepository()
        data = await repo.get_by_id(cohort_id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohort not found")
        return Cohort(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=Cohort, status_code=status.HTTP_201_CREATED)
async def create_cohort(
    payload: CohortCreate):
    try:
        repo = CohortRepository()
        created = await repo.create(payload)
        return Cohort(**created)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{cohort_id}", response_model=Cohort)
async def update_cohort(
    cohort_id: int,
    payload: CohortUpdate):
    try:
        repo = CohortRepository()
        existing = await repo.get_by_id(cohort_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohort not found")
        updated = await repo.update(cohort_id, payload)
        if not updated:
            return Cohort(**existing)
        return Cohort(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{cohort_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cohort(
    cohort_id: int):
    try:
        repo = CohortRepository()
        ok = await repo.delete(cohort_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohort not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


