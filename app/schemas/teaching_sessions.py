"""
Schemas for teaching_sessions table aligned with DB columns.
"""
from typing import Optional
from datetime import date, time, datetime
from enum import Enum
from pydantic import Field, validator

from app.schemas.base import (
    BaseSchema,
    CreateSchemaBase,
    UpdateSchemaBase,
    ResponseSchemaBase,
    TimestampSchema,
)


class SessionType(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    SEMINAR = "seminar"


class SessionStatus(str, Enum):
    OPEN = "Open"
    CLOSE = "Close"


class TeachingSessionBase(BaseSchema):
    class_id: int = Field(..., description="Class ID")
    session_date: date = Field(..., description="Session date")
    start_time: time = Field(..., description="Start time")
    end_time: time = Field(..., description="End time")
    session_type: SessionType = Field(..., description="Session type")
    qr_code: Optional[str] = Field(None, description="QR code for attendance")
    qr_expired_at: Optional[datetime] = Field(None, description="QR code expiry time")
    status: SessionStatus = Field(default=SessionStatus.CLOSE, description="Session status")

    @validator("end_time")
    def validate_time_range(cls, v, values):
        start = values.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class TeachingSessionCreate(TeachingSessionBase, CreateSchemaBase):
    pass


class TeachingSessionUpdate(UpdateSchemaBase):
    session_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    session_type: Optional[SessionType] = None
    qr_code: Optional[str] = None
    qr_expired_at: Optional[datetime] = None
    status: Optional[SessionStatus] = None


class TeachingSession(TeachingSessionBase, ResponseSchemaBase, TimestampSchema):
    pass


