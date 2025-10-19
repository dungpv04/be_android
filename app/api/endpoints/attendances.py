"""
Attendances API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List

from app.repositories.attendances import AttendanceRepository
from app.schemas.base import PaginatedResponse
from app.schemas.attendance import (
    Attendance,
    AttendanceCreate,
    AttendanceUpdate,
)


router = APIRouter(prefix="/attendances", tags=["attendances"])


@router.get("/", response_model=PaginatedResponse)
async def list_attendances(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")):
    try:
        repo = AttendanceRepository()
        items_data = await repo.get_all(skip=skip, limit=limit)
        items = [Attendance(**item) for item in items_data]
        total = len(items_data)
        return PaginatedResponse.create(items=items, total=total, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id}", response_model=Attendance)
async def get_attendance(
    id: int):
    try:
        repo = AttendanceRepository()
        data = await repo.get_by_id(id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
        return Attendance(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=Attendance, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    payload: AttendanceCreate):
    try:
        repo = AttendanceRepository()
        created = await repo.create(payload)
        return Attendance(**created)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id}", response_model=Attendance)
async def update_attendance(
    id: int,
    payload: AttendanceUpdate):
    try:
        repo = AttendanceRepository()
        existing = await repo.get_by_id(id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
        updated = await repo.update(id, payload)
        if not updated:
            return Attendance(**existing)
        return Attendance(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    id: int):
    try:
        repo = AttendanceRepository()
        ok = await repo.delete(id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/session/{session_id}", response_model=List[Attendance])
async def list_by_session(
    session_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)):
    try:
        repo = AttendanceRepository()
        items = await repo.get_by_session(session_id, skip=skip, limit=limit)
        return [Attendance(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/student/{student_id}", response_model=List[Attendance])
async def list_by_student(
    student_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)):
    try:
        repo = AttendanceRepository()
        items = await repo.get_by_student(student_id, skip=skip, limit=limit)
        return [Attendance(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


