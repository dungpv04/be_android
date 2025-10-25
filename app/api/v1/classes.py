from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import List
from datetime import date
import io
import qrcode
from supabase import Client
from app.core.database import get_supabase
from app.schemas import (
    ClassCreate, ClassUpdate, ClassResponse,
    TeachingSessionCreate, TeachingSessionUpdate, TeachingSessionResponse,
    AttendanceCreate, AttendanceUpdate, AttendanceResponse,
    ClassStudentCreate, ClassStudentResponse,
    BaseResponse, PaginatedResponse
)
from app.services import (
    ClassService, TeachingSessionService, AttendanceService,
    ClassStudentService
)

router = APIRouter(prefix="/classes", tags=["Classes"])


# Class endpoints
@router.post("", response_model=BaseResponse)
async def create_class(
    class_data: ClassCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new class."""
    try:
        class_service = ClassService(supabase)
        class_obj = await class_service.create(class_data.model_dump())
        
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create class"
            )
        
        return BaseResponse(
            message="Class created successfully",
            data={
                "id": class_obj.id,
                "name": class_obj.name,
                "code": class_obj.code
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create class error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("", response_model=PaginatedResponse)
async def get_classes(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    teacher_id: int = Query(None),
    subject_id: int = Query(None),
    active_only: bool = Query(True),
    supabase: Client = Depends(get_supabase)
):
    """Get all classes with pagination and optional filters."""
    try:
        class_service = ClassService(supabase)
        
        # Handle filters
        if teacher_id:
            classes = await class_service.get_by_teacher(teacher_id)
            return PaginatedResponse(
                items=[cls.model_dump() for cls in classes],
                total=len(classes),
                page=1,
                limit=len(classes),
                total_pages=1
            )
        elif subject_id:
            classes = await class_service.get_by_subject(subject_id)
            return PaginatedResponse(
                items=[cls.model_dump() for cls in classes],
                total=len(classes),
                page=1,
                limit=len(classes),
                total_pages=1
            )
        elif active_only:
            classes = await class_service.get_active_classes()
            return PaginatedResponse(
                items=[cls.model_dump() for cls in classes],
                total=len(classes),
                page=1,
                limit=len(classes),
                total_pages=1
            )
        else:
            result = await class_service.get_all(page, limit)
            return PaginatedResponse(
                items=[cls.model_dump() for cls in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get classes error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get class by ID."""
    try:
        class_service = ClassService(supabase)
        class_obj = await class_service.get_by_id(class_id)
        
        if not class_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
        
        return ClassResponse(**class_obj.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get class error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Teaching Session endpoints
@router.post("/{class_id}/sessions", response_model=BaseResponse)
async def create_teaching_session(
    class_id: int,
    session_data: TeachingSessionCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new teaching session for a class."""
    try:
        session_service = TeachingSessionService(supabase)
        
        # Ensure class_id matches
        session_dict = session_data.model_dump()
        session_dict["class_id"] = class_id
        
        session = await session_service.create(session_dict)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create teaching session"
            )
        
        return BaseResponse(
            message="Teaching session created successfully",
            data={
                "id": session.id,
                "session_date": session.session_date.isoformat(),
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat()
            }
        )
    except Exception as e:
        print(f"Create teaching session error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{class_id}/sessions", response_model=List[TeachingSessionResponse])
async def get_class_sessions(
    class_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get all teaching sessions for a class."""
    try:
        session_service = TeachingSessionService(supabase)
        sessions = await session_service.get_by_class(class_id)
        
        return [TeachingSessionResponse(**session.model_dump()) for session in sessions]
    except Exception as e:
        print(f"Get class sessions error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/sessions/{session_id}/qr-code", response_model=BaseResponse)
async def generate_session_qr_code(
    session_id: int,
    expiry_minutes: int = Query(30, ge=5, le=120),
    supabase: Client = Depends(get_supabase)
):
    """Generate QR code for a teaching session."""
    try:
        session_service = TeachingSessionService(supabase)
        qr_code = await session_service.generate_qr_code(session_id, expiry_minutes)
        
        if not qr_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teaching session not found"
            )
        
        return BaseResponse(
            message="QR code generated successfully",
            data={"qr_code": qr_code}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Generate QR code error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/sessions/{session_id}/qr-code")
async def get_session_qr_code_image(
    session_id: int,
    size: int = Query(200, ge=100, le=500, description="QR code size in pixels"),
    supabase: Client = Depends(get_supabase)
):
    """Get QR code image for a teaching session."""
    try:
        session_service = TeachingSessionService(supabase)
        
        # Get the session to verify it exists
        session = await session_service.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teaching session not found"
            )
        
        # Use the existing QR code if available, or generate a new one
        qr_data = session.qr_code
        if not qr_data:
            # Generate new QR code if none exists
            qr_data = await session_service.generate_qr_code(session_id, 30)
            if not qr_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate QR code"
                )
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Resize the image to the requested size
        qr_image = qr_image.resize((size, size))
        
        # Save image to bytes buffer
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        # Return image as streaming response
        return StreamingResponse(
            io.BytesIO(img_buffer.getvalue()),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=session_{session_id}_qr.png"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get QR code image error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Attendance endpoints
@router.post("/sessions/{session_id}/attendance", response_model=BaseResponse)
async def mark_attendance(
    session_id: int,
    attendance_data: AttendanceCreate,
    supabase: Client = Depends(get_supabase)
):
    """Mark attendance for a session (manual)."""
    try:
        attendance_service = AttendanceService(supabase)
        
        # Ensure session_id matches
        attendance_dict = attendance_data.model_dump()
        attendance_dict["session_id"] = session_id
        
        attendance = await attendance_service.mark_attendance_manual(
            session_id,
            attendance_data.student_id,
            attendance_data.status
        )
        
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to mark attendance"
            )
        
        return BaseResponse(message="Attendance marked successfully")
    except Exception as e:
        print(f"Mark attendance error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/sessions/{session_id}/attendance/qr", response_model=BaseResponse)
async def mark_attendance_by_qr(
    session_id: int,
    student_id: int,
    qr_code: str,
    supabase: Client = Depends(get_supabase)
):
    """Mark attendance using QR code."""
    try:
        attendance_service = AttendanceService(supabase)
        attendance = await attendance_service.mark_attendance_by_qr(
            session_id, student_id, qr_code
        )
        
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to mark attendance with QR code"
            )
        
        return BaseResponse(message="Attendance marked successfully using QR code")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Mark attendance by QR error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/sessions/{session_id}/attendance", response_model=List[AttendanceResponse])
async def get_session_attendance(
    session_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get all attendance records for a session."""
    try:
        attendance_service = AttendanceService(supabase)
        attendances = await attendance_service.get_by_session(session_id)
        
        return [AttendanceResponse(**attendance.model_dump()) for attendance in attendances]
    except Exception as e:
        print(f"Get session attendance error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{class_id}/attendance/statistics")
async def get_attendance_statistics(
    class_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    supabase: Client = Depends(get_supabase)
):
    """Get attendance statistics for a class within a date range."""
    try:
        attendance_service = AttendanceService(supabase)
        stats = await attendance_service.get_attendance_statistics(class_id, start_date, end_date)
        
        return BaseResponse(
            message="Attendance statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        print(f"Get attendance statistics error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Class Student enrollment endpoints
@router.post("/{class_id}/students", response_model=BaseResponse)
async def enroll_student(
    class_id: int,
    enrollment_data: ClassStudentCreate,
    supabase: Client = Depends(get_supabase)
):
    """Enroll a student in a class."""
    try:
        class_student_service = ClassStudentService(supabase)
        enrollment = await class_student_service.enroll_student(class_id, enrollment_data.student_id)
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to enroll student"
            )
        
        return BaseResponse(message="Student enrolled successfully")
    except Exception as e:
        print(f"Enroll student error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{class_id}/students", response_model=List[ClassStudentResponse])
async def get_class_students(
    class_id: int,
    active_only: bool = Query(True),
    supabase: Client = Depends(get_supabase)
):
    """Get all students enrolled in a class."""
    try:
        class_student_service = ClassStudentService(supabase)
        
        if active_only:
            enrollments = await class_student_service.get_active_enrollments(class_id)
        else:
            enrollments = await class_student_service.get_by_class(class_id)
        
        return [ClassStudentResponse(**enrollment.model_dump()) for enrollment in enrollments]
    except Exception as e:
        print(f"Get class students error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{class_id}/students/{student_id}", response_model=BaseResponse)
async def unenroll_student(
    class_id: int,
    student_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Unenroll a student from a class."""
    try:
        class_student_service = ClassStudentService(supabase)
        success = await class_student_service.unenroll_student(class_id, student_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student enrollment not found"
            )
        
        return BaseResponse(message="Student unenrolled successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unenroll student error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
