from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import date

class TeacherExcelRow(BaseModel):
    """Schema for teacher data from Excel file"""
    ho_ten: str  # Họ tên
    email: EmailStr  # Email
    so_dien_thoai: Optional[str] = None  # Số điện thoại
    dia_chi: Optional[str] = None  # Địa chỉ
    ngay_sinh: Optional[date] = None  # Ngày sinh
    que_quan: Optional[str] = None  # Quê quán
    khoa: str  # Khoa

class StudentExcelRow(BaseModel):
    """Schema for student data from Excel file"""
    ho_ten: str  # Họ tên
    email: EmailStr  # Email
    ma_sinh_vien: str  # Mã sinh viên
    so_dien_thoai: Optional[str] = None  # Số điện thoại
    dia_chi: Optional[str] = None  # Địa chỉ
    ngay_sinh: Optional[date] = None  # Ngày sinh
    que_quan: Optional[str] = None  # Quê quán
    lop: str  # Lớp

class BulkImportResult(BaseModel):
    """Result of bulk import operation"""
    total_rows: int
    successful: int
    failed: int
    errors: List[dict]
    created_users: List[dict]

class ExcelValidationError(BaseModel):
    """Validation error for Excel row"""
    row: int
    field: str
    error: str
    value: Optional[str] = None
