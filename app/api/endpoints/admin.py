"""
Admin API endpoints for user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
import uuid
import logging

from app.core.dependencies import get_admin_user
from app.core.auth_db import get_admin_user_db
from app.core.roles import UserRole

logger = logging.getLogger(__name__)
from app.services.supabase import SupabaseService
from app.repositories.teachers import TeacherRepository
from app.repositories.students import StudentRepository
from app.schemas.admin import (
    TeacherCreateRequest,
    StudentCreateRequest,
    TeacherCreateResponse,
    StudentCreateResponse,
    UserResponse, 
    UserListResponse
)
from app.schemas.users import TeacherCreate, StudentCreate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/teachers", response_model=TeacherCreateResponse)
async def create_teacher(
    teacher_data: TeacherCreateRequest
    # Temporarily remove admin authentication for testing
    # admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Create a new teacher with Supabase auth account."""
    try:
        supabase_service = SupabaseService()
        teacher_repo = TeacherRepository()
        
        # Check if teacher code already exists
        existing_teacher = await teacher_repo.get_by_teacher_code(teacher_data.teacher_code)
        if existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Teacher code '{teacher_data.teacher_code}' already exists"
            )
        
        # STEP 1: Validate DTO first (before creating account)
        from app.schemas.users import TeacherCreate
        # Use temporary UUID for validation
        import uuid
        temp_auth_id = uuid.uuid4()
        
        teacher_create_data = TeacherCreate(
            auth_id=temp_auth_id,
            teacher_code=teacher_data.teacher_code,
            full_name=teacher_data.full_name,
            phone=teacher_data.phone,
            birth_date=teacher_data.birth_date
        )
        # If we reach here, DTO validation passed
        
        # STEP 2: Create Supabase Auth account
        user_metadata = {
            "role": UserRole.TEACHER.value,
            "full_name": teacher_data.full_name,
            "teacher_code": teacher_data.teacher_code,
            "phone": teacher_data.phone,
            "birth_date": teacher_data.birth_date.isoformat() if teacher_data.birth_date else None
        }
        
        auth_result = await supabase_service.register_user(
            email=teacher_data.email,
            password=teacher_data.password,
            user_metadata=user_metadata
        )
        
        # STEP 3: Create teacher record with real auth_id
        teacher_create_data.auth_id = uuid.UUID(auth_result["id"])
        teacher_record = await teacher_repo.create(teacher_create_data)
        
        return TeacherCreateResponse(
            message="Teacher created successfully",
            auth_id=auth_result["id"],
            email=auth_result["email"],
            teacher_code=teacher_data.teacher_code,
            full_name=teacher_data.full_name,
            created_at=auth_result["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Teacher creation failed: {str(e)}"
        )


@router.post("/students", response_model=StudentCreateResponse)
async def create_student(
    student_data: StudentCreateRequest
    # Temporarily remove admin authentication for testing
    # admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Create a new student with Supabase auth account."""
    try:
        supabase_service = SupabaseService()
        student_repo = StudentRepository()
        
        # Check if student code already exists
        existing_student = await student_repo.get_by_student_code(student_data.student_code)
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student code '{student_data.student_code}' already exists"
            )
        
        # STEP 1: Validate DTO first (before creating account)
        from app.schemas.users import StudentCreate
        # Use temporary UUID for validation
        import uuid
        temp_auth_id = uuid.uuid4()
        
        student_create_data = StudentCreate(
            auth_id=temp_auth_id,
            student_code=student_data.student_code,
            full_name=student_data.full_name,
            phone=student_data.phone,
            birth_date=student_data.birth_date,
            major_id=student_data.major_id,
            cohort_id=student_data.cohort_id,
            class_id=student_data.class_id
        )
        # If we reach here, DTO validation passed
        
        # STEP 2: Create Supabase Auth account
        user_metadata = {
            "role": UserRole.STUDENT.value,
            "full_name": student_data.full_name,
            "student_code": student_data.student_code,
            "phone": student_data.phone,
            "birth_date": student_data.birth_date.isoformat() if student_data.birth_date else None,
            "major_id": student_data.major_id,
            "cohort_id": student_data.cohort_id,
            "class_id": student_data.class_id
        }
        
        auth_result = await supabase_service.register_user(
            email=student_data.email,
            password=student_data.password,
            user_metadata=user_metadata
        )
        
        # STEP 3: Create student record with real auth_id
        student_create_data.auth_id = uuid.UUID(auth_result["id"])
        student_record = await student_repo.create(student_create_data)
        
        return StudentCreateResponse(
            message="Student created successfully",
            auth_id=auth_result["id"],
            email=auth_result["email"],
            student_code=student_data.student_code,
            full_name=student_data.full_name,
            major_id=student_data.major_id,
            cohort_id=student_data.cohort_id,
            class_id=student_data.class_id,
            created_at=auth_result["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Student creation failed: {str(e)}"
        )


# Teacher Management Endpoints
@router.get("/teachers")
async def list_teachers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """List all teachers with pagination."""
    try:
        teacher_repo = TeacherRepository()
        teachers = await teacher_repo.get_all(skip=skip, limit=limit)
        return {"teachers": teachers, "total": len(teachers)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list teachers: {str(e)}"
        )


@router.get("/teachers/{teacher_id}")
async def get_teacher(
    teacher_id: int,
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """Get a specific teacher by ID."""
    try:
        teacher_repo = TeacherRepository()
        teacher = await teacher_repo.get_by_id(teacher_id)
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        return teacher
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teacher: {str(e)}"
        )


@router.put("/teachers/{teacher_id}")
async def update_teacher(
    teacher_id: int,
    teacher_data: Dict[str, Any],
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """Update a teacher's information."""
    try:
        from app.schemas.users import TeacherUpdate
        teacher_repo = TeacherRepository()
        
        # Validate update data
        teacher_update = TeacherUpdate(**teacher_data)
        
        # Update teacher record
        updated_teacher = await teacher_repo.update(teacher_id, teacher_update)
        
        if not updated_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        return {"message": "Teacher updated successfully", "teacher": updated_teacher}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update teacher: {str(e)}"
        )


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """Delete a teacher and their auth account."""
    try:
        teacher_repo = TeacherRepository()
        supabase_service = SupabaseService()
        
        # Get teacher info before deletion
        teacher = await teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        # Delete from auth
        try:
            await supabase_service.admin_delete_user(str(teacher["auth_id"]))
        except Exception as auth_error:
            # Log but continue - database record should still be deleted
            logger.warning(f"Failed to delete auth user: {auth_error}")
        
        # Delete teacher record
        await teacher_repo.delete(teacher_id)
        
        return {"message": "Teacher deleted successfully", "deleted_id": teacher_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete teacher: {str(e)}"
        )


# Student Management Endpoints
@router.get("/students")
async def list_students(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    major_id: Optional[int] = Query(None, description="Filter by major"),
    cohort_id: Optional[int] = Query(None, description="Filter by cohort"),
    class_id: Optional[int] = Query(None, description="Filter by class"),
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """List all students with pagination and filtering."""
    try:
        student_repo = StudentRepository()
        
        if major_id:
            students = await student_repo.get_by_major(major_id, skip=skip, limit=limit)
        elif cohort_id:
            students = await student_repo.get_by_cohort(cohort_id, skip=skip, limit=limit)
        elif class_id:
            students = await student_repo.get_by_class(class_id, skip=skip, limit=limit)
        else:
            students = await student_repo.get_all(skip=skip, limit=limit)
            
        return {"students": students, "total": len(students)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list students: {str(e)}"
        )


@router.get("/students/{student_id}")
async def get_student(
    student_id: int,
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """Get a specific student by ID."""
    try:
        student_repo = StudentRepository()
        student = await student_repo.get_by_id(student_id)
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        return student
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student: {str(e)}"
        )


@router.put("/students/{student_id}")
async def update_student(
    student_id: int,
    student_data: Dict[str, Any],
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """Update a student's information."""
    try:
        from app.schemas.users import StudentUpdate
        student_repo = StudentRepository()
        
        # Validate update data
        student_update = StudentUpdate(**student_data)
        
        # Update student record
        updated_student = await student_repo.update(student_id, student_update)
        
        if not updated_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        return {"message": "Student updated successfully", "student": updated_student}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update student: {str(e)}"
        )


@router.delete("/students/{student_id}")
async def delete_student(
    student_id: int,
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """Delete a student and their auth account."""
    try:
        student_repo = StudentRepository()
        supabase_service = SupabaseService()
        
        # Get student info before deletion
        student = await student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Delete from auth
        try:
            await supabase_service.admin_delete_user(str(student["auth_id"]))
        except Exception as auth_error:
            # Log but continue - database record should still be deleted
            logger.warning(f"Failed to delete auth user: {auth_error}")
        
        # Delete student record
        await student_repo.delete(student_id)
        
        return {"message": "Student deleted successfully", "deleted_id": student_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete student: {str(e)}"
        )


# Bulk Operations
@router.post("/teachers/bulk")
async def bulk_teacher_operation(
    operation_data: Dict[str, Any],
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """Perform bulk operations on multiple teachers."""
    try:
        teacher_repo = TeacherRepository()
        supabase_service = SupabaseService()
        
        operation = operation_data.get("operation")
        teacher_ids = operation_data.get("teacher_ids", [])
        
        successful = 0
        failed = 0
        errors = []
        successful_ids = []
        
        for teacher_id in teacher_ids:
            try:
                if operation == "delete":
                    teacher = await teacher_repo.get_by_id(teacher_id)
                    if teacher:
                        # Delete auth user
                        try:
                            await supabase_service.admin_delete_user(str(teacher["auth_id"]))
                        except Exception:
                            pass  # Continue even if auth deletion fails
                        
                        # Delete teacher record
                        await teacher_repo.delete(teacher_id)
                        successful += 1
                        successful_ids.append(teacher_id)
                    else:
                        failed += 1
                        errors.append(f"Teacher {teacher_id}: Not found")
                
            except Exception as e:
                failed += 1
                errors.append(f"Teacher {teacher_id}: {str(e)}")
        
        return {
            "operation": operation,
            "total_requested": len(teacher_ids),
            "successful": successful,
            "failed": failed,
            "errors": errors,
            "successful_ids": successful_ids
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk teacher operation failed: {str(e)}"
        )


@router.post("/students/bulk")
async def bulk_student_operation(
    operation_data: Dict[str, Any],
    admin_user: Dict[str, Any] = Depends(get_admin_user_db)
):
    """Perform bulk operations on multiple students."""
    try:
        student_repo = StudentRepository()
        supabase_service = SupabaseService()
        
        operation = operation_data.get("operation")
        student_ids = operation_data.get("student_ids", [])
        
        successful = 0
        failed = 0
        errors = []
        successful_ids = []
        
        for student_id in student_ids:
            try:
                if operation == "delete":
                    student = await student_repo.get_by_id(student_id)
                    if student:
                        # Delete auth user
                        try:
                            await supabase_service.admin_delete_user(str(student["auth_id"]))
                        except Exception:
                            pass  # Continue even if auth deletion fails
                        
                        # Delete student record
                        await student_repo.delete(student_id)
                        successful += 1
                        successful_ids.append(student_id)
                    else:
                        failed += 1
                        errors.append(f"Student {student_id}: Not found")
                
            except Exception as e:
                failed += 1
                errors.append(f"Student {student_id}: {str(e)}")
        
        return {
            "operation": operation,
            "total_requested": len(student_ids),
            "successful": successful,
            "failed": failed,
            "errors": errors,
            "successful_ids": successful_ids
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk student operation failed: {str(e)}"
        )


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of users per page"),
    role: UserRole = Query(None, description="Filter by role"),
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """List all users with pagination and filtering."""
    try:
        supabase_service = SupabaseService()
        
        # Get users from Supabase
        result = await supabase_service.admin_list_users(page=page, per_page=page_size)
        
        users = []
        for user_data in result["users"]:
            user_metadata = user_data.get("user_metadata", {})
            user_role = user_metadata.get("role", UserRole.STUDENT)
            
            # Filter by role if specified
            if role and user_role != role.value:
                continue
            
            users.append(UserResponse(
                auth_id=user_data["id"],
                email=user_data["email"],
                role=UserRole(user_role),
                full_name=user_metadata.get("full_name", ""),
                phone=user_metadata.get("phone"),
                birth_date=user_metadata.get("birth_date"),
                created_at=user_data["created_at"],
                teacher_code=user_metadata.get("teacher_code"),
                student_code=user_metadata.get("student_code"),
                major_id=user_metadata.get("major_id"),
                cohort_id=user_metadata.get("cohort_id")
            ))
        
        return UserListResponse(
            users=users,
            total=len(users),
            page=page,
            page_size=page_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Get a specific user by ID."""
    try:
        supabase_service = SupabaseService()
        
        user_data = await supabase_service.get_user_by_id(str(user_id))
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_metadata = user_data.get("user_metadata", {})
        
        return UserResponse(
            auth_id=user_data["id"],
            email=user_data["email"],
            role=UserRole(user_metadata.get("role", UserRole.STUDENT)),
            full_name=user_metadata.get("full_name", ""),
            phone=user_metadata.get("phone"),
            birth_date=user_metadata.get("birth_date"),
            created_at=user_data.get("created_at"),
            teacher_code=user_metadata.get("teacher_code"),
            student_code=user_metadata.get("student_code"),
            major_id=user_metadata.get("major_id"),
            cohort_id=user_metadata.get("cohort_id")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )



@router.get("/stats")
async def get_admin_stats(
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Get admin dashboard statistics."""
    try:
        supabase_service = SupabaseService()
        
        # Get all users
        result = await supabase_service.admin_list_users(per_page=1000)
        
        # Count by roles
        role_counts = {
            UserRole.ADMIN: 0,
            UserRole.TEACHER: 0,
            UserRole.STUDENT: 0
        }
        
        for user in result["users"]:
            user_role = user.get("user_metadata", {}).get("role", UserRole.STUDENT)
            if user_role in role_counts:
                role_counts[UserRole(user_role)] += 1
        
        return {
            "total_users": result["total"],
            "users_by_role": {
                "admin": role_counts[UserRole.ADMIN],
                "teacher": role_counts[UserRole.TEACHER],
                "student": role_counts[UserRole.STUDENT]
            },
            "recent_registrations": len([
                u for u in result["users"] 
                if u.get("created_at") # Could add date filtering here
            ])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
