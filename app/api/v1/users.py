from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from supabase import Client
from app.core.database import get_supabase
from app.schemas import (
    StudentCreate, StudentUpdate, StudentResponse,
    TeacherCreate, TeacherUpdate, TeacherResponse,
    BaseResponse, PaginatedResponse
)
from app.services import StudentService, TeacherService

router = APIRouter(prefix="/users", tags=["Users"])


# Student endpoints
@router.post("/students", response_model=BaseResponse)
async def create_student(
    student_data: StudentCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new student with authentication."""
    try:
        student_service = StudentService(supabase)
        student = await student_service.create_student_with_auth(student_data)
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create student"
            )
        
        return BaseResponse(
            message="Student created successfully",
            data={
                "id": student.id,
                "student_code": student.student_code,
                "full_name": student.full_name
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create student error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/students", response_model=PaginatedResponse)
async def get_students(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    faculty_id: int = Query(None),
    major_id: int = Query(None),
    cohort_id: int = Query(None),
    class_name: str = Query(None),
    search: str = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all students with pagination and optional filters."""
    try:
        student_service = StudentService(supabase)
        
        # Handle search
        if search:
            students = await student_service.search_by_name(search)
            return PaginatedResponse(
                items=[student.model_dump() for student in students],
                total=len(students),
                page=1,
                limit=len(students),
                total_pages=1
            )
        
        # Handle filters
        if faculty_id:
            students = await student_service.get_by_faculty(faculty_id)
            return PaginatedResponse(
                items=[student.model_dump() for student in students],
                total=len(students),
                page=1,
                limit=len(students),
                total_pages=1
            )
        elif major_id:
            students = await student_service.get_by_major(major_id)
            return PaginatedResponse(
                items=[student.model_dump() for student in students],
                total=len(students),
                page=1,
                limit=len(students),
                total_pages=1
            )
        elif cohort_id:
            students = await student_service.get_by_cohort(cohort_id)
            return PaginatedResponse(
                items=[student.model_dump() for student in students],
                total=len(students),
                page=1,
                limit=len(students),
                total_pages=1
            )
        elif class_name:
            students = await student_service.get_by_class_name(class_name)
            return PaginatedResponse(
                items=[student.model_dump() for student in students],
                total=len(students),
                page=1,
                limit=len(students),
                total_pages=1
            )
        else:
            result = await student_service.get_all(page, limit)
            return PaginatedResponse(
                items=[student.model_dump() for student in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get students error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get student by ID."""
    try:
        student_service = StudentService(supabase)
        student = await student_service.get_by_id(student_id)
        
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        return StudentResponse(**student.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get student error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/students/code/{student_code}", response_model=StudentResponse)
async def get_student_by_code(
    student_code: str,
    supabase: Client = Depends(get_supabase)
):
    """Get student by student code."""
    try:
        student_service = StudentService(supabase)
        student = await student_service.get_by_student_code(student_code)
        
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        return StudentResponse(**student.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get student by code error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/students/{student_id}", response_model=BaseResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update student by ID."""
    try:
        student_service = StudentService(supabase)
        student = await student_service.update(student_id, student_data.model_dump(exclude_none=True))
        
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        return BaseResponse(message="Student updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update student error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/students/{student_id}", response_model=BaseResponse)
async def delete_student(
    student_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete student by ID."""
    try:
        student_service = StudentService(supabase)
        success = await student_service.delete(student_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        return BaseResponse(message="Student deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete student error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Teacher endpoints
@router.post("/teachers", response_model=BaseResponse)
async def create_teacher(
    teacher_data: TeacherCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new teacher with authentication."""
    try:
        teacher_service = TeacherService(supabase)
        teacher = await teacher_service.create_teacher_with_auth(teacher_data)
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create teacher"
            )
        
        return BaseResponse(
            message="Teacher created successfully",
            data={
                "id": teacher.id,
                "teacher_code": teacher.teacher_code,
                "full_name": teacher.full_name
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create teacher error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/teachers", response_model=PaginatedResponse)
async def get_teachers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    faculty_id: int = Query(None),
    department_id: int = Query(None),
    search: str = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all teachers with pagination and optional filters."""
    try:
        teacher_service = TeacherService(supabase)
        
        # Handle search
        if search:
            teachers = await teacher_service.search_by_name(search)
            return PaginatedResponse(
                items=[teacher.model_dump() for teacher in teachers],
                total=len(teachers),
                page=1,
                limit=len(teachers),
                total_pages=1
            )
        
        # Handle filters
        if faculty_id:
            teachers = await teacher_service.get_by_faculty(faculty_id)
            return PaginatedResponse(
                items=[teacher.model_dump() for teacher in teachers],
                total=len(teachers),
                page=1,
                limit=len(teachers),
                total_pages=1
            )
        elif department_id:
            teachers = await teacher_service.get_by_department(department_id)
            return PaginatedResponse(
                items=[teacher.model_dump() for teacher in teachers],
                total=len(teachers),
                page=1,
                limit=len(teachers),
                total_pages=1
            )
        else:
            result = await teacher_service.get_all(page, limit)
            return PaginatedResponse(
                items=[teacher.model_dump() for teacher in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get teachers error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get teacher by ID."""
    try:
        teacher_service = TeacherService(supabase)
        teacher = await teacher_service.get_by_id(teacher_id)
        
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
        
        return TeacherResponse(**teacher.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get teacher error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
