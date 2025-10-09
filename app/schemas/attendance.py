"""
Attendance and face recognition schemas.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from pydantic import Field, validator
from enum import Enum

from app.schemas.base import (
    BaseSchema, 
    CreateSchemaBase, 
    UpdateSchemaBase, 
    ResponseSchemaBase, 
    TimestampSchema
)
from app.schemas.users import Student
from app.schemas.classes import TeachingSession


class AttendanceStatus(str, Enum):
    """Attendance status enumeration."""
    
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    EARLY_DEPARTURE = "early_departure"


class AttendanceMethod(str, Enum):
    """Attendance marking method enumeration."""
    
    QR_CODE = "qr_code"
    FACE_RECOGNITION = "face_recognition"
    MANUAL = "manual"
    BULK_IMPORT = "bulk_import"


# Attendance schemas
class AttendanceBase(BaseSchema):
    """Base attendance schema."""
    
    session_id: int = Field(..., description="Teaching session ID")
    student_id: int = Field(..., description="Student ID")
    status: AttendanceStatus = Field(..., description="Attendance status")
    check_in_time: Optional[datetime] = Field(None, description="Check-in timestamp")
    check_out_time: Optional[datetime] = Field(None, description="Check-out timestamp")
    method: AttendanceMethod = Field(default=AttendanceMethod.MANUAL, description="Attendance method")
    location: Optional[str] = Field(None, max_length=255, description="Check-in location")
    notes: Optional[str] = Field(None, max_length=500, description="Attendance notes")
    is_late: bool = Field(default=False, description="Whether student was late")
    late_minutes: Optional[int] = Field(None, ge=0, description="Minutes late")
    
    @validator('check_out_time')
    def validate_checkout_time(cls, v, values):
        check_in_time = values.get('check_in_time')
        if check_in_time and v and v <= check_in_time:
            raise ValueError('Check-out time must be after check-in time')
        return v
    
    @validator('late_minutes')
    def validate_late_minutes(cls, v, values):
        is_late = values.get('is_late', False)
        if is_late and v is None:
            raise ValueError('Late minutes must be specified when student is late')
        if not is_late and v is not None and v > 0:
            raise ValueError('Late minutes should be 0 or None when student is not late')
        return v


class AttendanceCreate(AttendanceBase, CreateSchemaBase):
    """Schema for creating attendance record."""
    
    auto_detect_late: bool = Field(default=True, description="Auto-detect if student is late")


class AttendanceUpdate(UpdateSchemaBase):
    """Schema for updating attendance record."""
    
    status: Optional[AttendanceStatus] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    method: Optional[AttendanceMethod] = None
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=500)
    is_late: Optional[bool] = None
    late_minutes: Optional[int] = Field(None, ge=0)
    
    @validator('check_out_time')
    def validate_checkout_time(cls, v, values):
        check_in_time = values.get('check_in_time')
        if check_in_time and v and v <= check_in_time:
            raise ValueError('Check-out time must be after check-in time')
        return v


class Attendance(AttendanceBase, ResponseSchemaBase, TimestampSchema):
    """Attendance response schema."""
    
    student: Optional[Student] = None
    session: Optional[TeachingSession] = None
    duration_minutes: Optional[int] = Field(None, description="Session duration in minutes")


# Bulk attendance operations
class BulkAttendanceCreate(BaseSchema):
    """Schema for bulk attendance creation."""
    
    session_id: int = Field(..., description="Teaching session ID")
    attendances: List[Dict[str, Any]] = Field(..., description="List of attendance records")
    method: AttendanceMethod = Field(default=AttendanceMethod.BULK_IMPORT)
    notes: Optional[str] = Field(None, max_length=500, description="Bulk operation notes")
    
    @validator('attendances')
    def validate_attendances(cls, v):
        if not v:
            raise ValueError('At least one attendance record is required')
        if len(v) > 1000:
            raise ValueError('Cannot process more than 1000 attendance records at once')
        
        required_fields = ['student_id', 'status']
        for i, attendance in enumerate(v):
            for field in required_fields:
                if field not in attendance:
                    raise ValueError(f'Attendance record {i} missing required field: {field}')
        return v


class BulkAttendanceResponse(BaseSchema):
    """Response schema for bulk attendance operations."""
    
    total_processed: int
    successful: int
    failed: int
    errors: List[str] = []
    created_ids: List[int] = []


# QR Code attendance
class QRAttendanceCreate(BaseSchema):
    """Schema for QR code attendance."""
    
    qr_code: str = Field(..., description="QR code value")
    location: Optional[str] = Field(None, max_length=255, description="Check-in location")
    check_in_time: Optional[datetime] = Field(None, description="Check-in time (defaults to now)")


# Face recognition schemas
class FaceTemplateBase(BaseSchema):
    """Base face template schema."""
    
    student_id: int = Field(..., description="Student ID")
    template_name: str = Field(..., min_length=1, max_length=100, description="Template name")
    face_encoding: str = Field(..., description="Encoded face data (base64)")
    confidence_threshold: float = Field(default=0.6, ge=0.1, le=1.0, description="Recognition confidence threshold")
    is_active: bool = Field(default=True, description="Whether template is active")
    notes: Optional[str] = Field(None, max_length=500, description="Template notes")
    
    @validator('face_encoding')
    def validate_face_encoding(cls, v):
        # Basic validation - in real implementation, you'd validate the encoding format
        if len(v) < 100:  # Minimum length for a reasonable face encoding
            raise ValueError('Face encoding appears to be too short')
        return v


class FaceTemplateCreate(FaceTemplateBase, CreateSchemaBase):
    """Schema for creating face template."""
    
    image_data: Optional[str] = Field(None, description="Base64 encoded image for processing")


class FaceTemplateUpdate(UpdateSchemaBase):
    """Schema for updating face template."""
    
    template_name: Optional[str] = Field(None, min_length=1, max_length=100)
    face_encoding: Optional[str] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.1, le=1.0)
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class FaceTemplate(FaceTemplateBase, ResponseSchemaBase, TimestampSchema):
    """Face template response schema."""
    
    student: Optional[Student] = None
    usage_count: Optional[int] = Field(None, description="Number of times used for recognition")
    last_used: Optional[datetime] = Field(None, description="Last recognition timestamp")


class FaceRecognitionRequest(BaseSchema):
    """Schema for face recognition attendance."""
    
    session_id: int = Field(..., description="Teaching session ID")
    image_data: str = Field(..., description="Base64 encoded image")
    location: Optional[str] = Field(None, max_length=255, description="Check-in location")
    confidence_threshold: Optional[float] = Field(None, ge=0.1, le=1.0, description="Override default threshold")


class FaceRecognitionResponse(BaseSchema):
    """Response schema for face recognition."""
    
    success: bool = Field(..., description="Whether recognition was successful")
    student_id: Optional[int] = Field(None, description="Recognized student ID")
    confidence: Optional[float] = Field(None, description="Recognition confidence")
    attendance_id: Optional[int] = Field(None, description="Created attendance record ID")
    message: str = Field(..., description="Result message")


# Attendance reports and analytics
class AttendanceReportFilter(BaseSchema):
    """Filter schema for attendance reports."""
    
    class_id: Optional[int] = None
    student_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[AttendanceStatus] = None
    method: Optional[AttendanceMethod] = None
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('End date must be after start date')
        return v


class AttendanceReportSummary(BaseSchema):
    """Attendance report summary schema."""
    
    total_sessions: int
    total_attendances: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_rate: float
    average_late_minutes: Optional[float] = None
    most_common_method: Optional[AttendanceMethod] = None


class StudentAttendanceReport(BaseSchema):
    """Individual student attendance report."""
    
    student_id: int
    student_name: str
    class_id: int
    class_name: str
    summary: AttendanceReportSummary
    recent_attendances: List[Attendance] = []
    trends: Optional[Dict[str, Any]] = None


class ClassAttendanceReport(BaseSchema):
    """Class-wide attendance report."""
    
    class_id: int
    class_name: str
    summary: AttendanceReportSummary
    student_summaries: List[Dict[str, Any]] = []
    session_summaries: List[Dict[str, Any]] = []
    trends: Optional[Dict[str, Any]] = None


# Attendance notifications
class AttendanceNotification(BaseSchema):
    """Attendance notification schema."""
    
    student_id: int
    session_id: int
    notification_type: str = Field(..., description="Type: absent, late, reminder")
    message: str = Field(..., description="Notification message")
    sent_at: Optional[datetime] = None
    delivery_method: str = Field(default="email", description="email, sms, push")


class AttendanceReminder(BaseSchema):
    """Attendance reminder schema."""
    
    session_id: int = Field(..., description="Teaching session ID")
    reminder_minutes: int = Field(default=30, ge=5, le=1440, description="Minutes before session")
    message_template: Optional[str] = Field(None, description="Custom reminder message")
    include_qr_code: bool = Field(default=True, description="Include QR code in reminder")
