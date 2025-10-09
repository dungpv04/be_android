"""
Admin API endpoints for user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List
import uuid

from app.core.dependencies import get_admin_user
from app.core.roles import UserRole
from app.services.supabase import SupabaseService
from app.repositories.teachers import TeacherRepository
from app.repositories.students import StudentRepository
from app.schemas.admin import (
    TeacherCreateRequest,
    StudentCreateRequest,
    TeacherCreateResponse,
    StudentCreateResponse,
    UserUpdateRequest, 
    UserResponse, 
    UserListResponse,
    UserDeleteResponse,
    BulkUserOperation,
    BulkOperationResponse
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
        
        # Prepare teacher metadata
        user_metadata = {
            "role": UserRole.TEACHER.value,
            "full_name": teacher_data.full_name,
            "teacher_code": teacher_data.teacher_code,
            "phone": teacher_data.phone,
            "birth_date": teacher_data.birth_date.isoformat() if teacher_data.birth_date else None
        }
        
        # Create user in Supabase Auth
        auth_result = await supabase_service.admin_create_user(
            email=teacher_data.email,
            password=teacher_data.password,
            user_metadata=user_metadata
        )
        
        # Create corresponding record in teachers table
        from app.schemas.users import TeacherCreate
        teacher_create_data = TeacherCreate(
            auth_id=uuid.UUID(auth_result["id"]),
            teacher_code=teacher_data.teacher_code,
            full_name=teacher_data.full_name,
            phone=teacher_data.phone,
            birth_date=teacher_data.birth_date
        )
        
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
        
        # Prepare student metadata
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
        
        # Create user in Supabase Auth
        auth_result = await supabase_service.admin_create_user(
            email=student_data.email,
            password=student_data.password,
            user_metadata=user_metadata
        )
        
        # Create corresponding record in students table
        from app.schemas.users import StudentCreate
        student_create_data = StudentCreate(
            auth_id=uuid.UUID(auth_result["id"]),
            student_code=student_data.student_code,
            full_name=student_data.full_name,
            phone=student_data.phone,
            birth_date=student_data.birth_date,
            major_id=student_data.major_id,
            cohort_id=student_data.cohort_id,
            class_id=student_data.class_id
        )
        
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


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdateRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Update a user's information."""
    try:
        supabase_service = SupabaseService()
        
        # Prepare update data
        update_metadata = {}
        if user_data.full_name:
            update_metadata["full_name"] = user_data.full_name
        if user_data.phone:
            update_metadata["phone"] = user_data.phone
        if user_data.birth_date:
            update_metadata["birth_date"] = user_data.birth_date.isoformat()
        if user_data.teacher_code:
            update_metadata["teacher_code"] = user_data.teacher_code
        if user_data.student_code:
            update_metadata["student_code"] = user_data.student_code
        if user_data.major_id:
            update_metadata["major_id"] = user_data.major_id
        if user_data.cohort_id:
            update_metadata["cohort_id"] = user_data.cohort_id
        
        # Update user in Supabase
        result = await supabase_service.admin_update_user(
            user_id=str(user_id),
            email=user_data.email,
            user_metadata=update_metadata if update_metadata else None
        )
        
        user_metadata = result.get("user_metadata", {})
        
        return UserResponse(
            auth_id=result["id"],
            email=result["email"],
            role=UserRole(user_metadata.get("role", UserRole.STUDENT)),
            full_name=user_metadata.get("full_name", ""),
            phone=user_metadata.get("phone"),
            birth_date=user_metadata.get("birth_date"),
            created_at=user_metadata.get("created_at"),
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
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/users/{user_id}", response_model=UserDeleteResponse)
async def delete_user(
    user_id: uuid.UUID,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Delete a user and their auth account."""
    try:
        supabase_service = SupabaseService()
        
        # Get user info before deletion
        user_data = await supabase_service.get_user_by_id(str(user_id))
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_role = user_data.get("user_metadata", {}).get("role", UserRole.STUDENT)
        
        # Delete from Supabase Auth
        await supabase_service.admin_delete_user(str(user_id))
        
        # TODO: Delete corresponding record from teacher/student table
        # This would be done through your repository layer
        
        return UserDeleteResponse(
            message="User deleted successfully",
            deleted_auth_id=user_id,
            deleted_role=UserRole(user_role)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.post("/users/bulk", response_model=BulkOperationResponse)
async def bulk_user_operation(
    operation_data: BulkUserOperation,
    admin_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Perform bulk operations on multiple users."""
    try:
        supabase_service = SupabaseService()
        
        successful = 0
        failed = 0
        errors = []
        successful_ids = []
        
        for user_id in operation_data.user_ids:
            try:
                if operation_data.operation == "delete":
                    await supabase_service.admin_delete_user(str(user_id))
                    successful += 1
                    successful_ids.append(user_id)
                # Add more operations as needed (activate, deactivate)
                
            except Exception as e:
                failed += 1
                errors.append(f"User {user_id}: {str(e)}")
        
        return BulkOperationResponse(
            operation=operation_data.operation,
            total_requested=len(operation_data.user_ids),
            successful=successful,
            failed=failed,
            errors=errors,
            successful_ids=successful_ids
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk operation failed: {str(e)}"
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
