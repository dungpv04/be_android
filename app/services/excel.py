"""Excel processing service for bulk user imports."""

import pandas as pd
import string
import secrets
from io import BytesIO
from typing import List, Dict, Any, Tuple
from datetime import datetime, date
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
import logging

from ..schemas.excel import TeacherExcelRow, StudentExcelRow, BulkImportResult, ExcelValidationError
from ..schemas.users import TeacherCreate, StudentCreate
from ..repositories.academic import AcademicRepository
from ..repositories.users import UserRepository
from ..repositories.classes import ClassRepository
from ..services.users import StudentService, TeacherService

logger = logging.getLogger(__name__)

class ExcelService:
    def __init__(self, user_repo: UserRepository, academic_repo: AcademicRepository, class_repo: ClassRepository):
        self.user_repo = user_repo
        self.academic_repo = academic_repo
        self.class_repo = class_repo
        # Initialize services for user creation with auth
        self.student_service = None
        self.teacher_service = None
    
    def _get_student_service(self):
        """Lazy initialization of student service to avoid circular import."""
        if self.student_service is None:
            self.student_service = StudentService(self.user_repo.supabase)
        return self.student_service
    
    def _get_teacher_service(self):
        """Lazy initialization of teacher service to avoid circular import."""
        if self.teacher_service is None:
            self.teacher_service = TeacherService(self.user_repo.supabase)
        return self.teacher_service
    
    def _generate_random_password(self) -> str:
        """Generate a 6-character random password."""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(6))

    def generate_teacher_sample_excel(self) -> BytesIO:
        """Generate sample Excel file for teacher import with Vietnamese headers."""
        sample_data = {
            'Họ tên': ['Nguyễn Văn A', 'Trần Thị B'],
            'Email': ['nguyenvana@email.com', 'tranthib@email.com'],
            'Số điện thoại': ['0901234567', '0987654321'],
            'Địa chỉ': ['123 Đường ABC, Quận 1, TP.HCM', '456 Đường XYZ, Quận 2, TP.HCM'],
            'Ngày sinh': ['1985-01-15', '1987-03-20'],
            'Quê quán': ['Hà Nội', 'TP. Hồ Chí Minh'],
            'Khoa': ['Công nghệ thông tin', 'Kinh tế'],
            'Bộ môn': ['Khoa học máy tính', 'Quản trị kinh doanh']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Giảng viên', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Giảng viên']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output

    def generate_student_sample_excel(self) -> BytesIO:
        """Generate sample Excel file for student import with Vietnamese headers."""
        sample_data = {
            'Họ tên': ['Lê Văn C', 'Phạm Thị D'],
            'Email': ['levanc@student.edu.vn', 'phamthid@student.edu.vn'],
            'Mã sinh viên': ['SV001', 'SV002'],
            'Số điện thoại': ['0912345678', '0976543210'],
            'Địa chỉ': ['789 Đường DEF, Quận 3, TP.HCM', '101 Đường GHI, Quận 4, TP.HCM'],
            'Ngày sinh': ['2000-05-10', '2001-08-25'],
            'Quê quán': ['Đà Nẵng', 'Cần Thơ'],
            'Lớp': ['CNTT01', 'KTDN02'],
            'Khoa': ['Công nghệ thông tin', 'Kinh tế'],
            'Ngành': ['Công nghệ phần mềm', 'Quản trị kinh doanh'],
            'Khóa': ['K2020', 'K2021']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sinh viên', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Sinh viên']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output

    async def process_teacher_excel(self, file: UploadFile) -> BulkImportResult:
        """Process Excel file for bulk teacher creation."""
        try:
            # Read Excel file
            content = await file.read()
            df = pd.read_excel(BytesIO(content))
            
            # Validate required columns
            required_columns = ['Họ tên', 'Email', 'Khoa']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required columns: {', '.join(missing_columns)}"
                )
            
            # Process each row
            results = []
            errors = []
            created_users = []
            teacher_passwords = []  # Store passwords for Excel response
            
            for index, row in df.iterrows():
                try:
                    # Validate and convert data
                    teacher_data = await self._validate_teacher_row(row, index + 2)  # +2 for header row
                    
                    # Check if faculty exists
                    faculty = await self.academic_repo.get_faculty_by_name(teacher_data['faculty_name'])
                    if not faculty:
                        errors.append({
                            "row": index + 2,
                            "field": "Khoa",
                            "error": f"Faculty '{teacher_data['faculty_name']}' not found",
                            "value": teacher_data['faculty_name']
                        })
                        continue
                    
                    # Look up department if provided
                    department_id = None
                    if teacher_data.get('department_name'):
                        department = await self.academic_repo.get_department_by_name(teacher_data['department_name'])
                        if department:
                            department_id = department.id
                        else:
                            errors.append({
                                "row": index + 2,
                                "field": "Bộ môn",
                                "error": f"Department '{teacher_data['department_name']}' not found",
                                "value": teacher_data['department_name']
                            })
                            continue
                    
                    # Generate random password and teacher code
                    random_password = self._generate_random_password()
                    teacher_code = teacher_data['email'].split('@')[0]
                    
                    # Create teacher
                    teacher_create = TeacherCreate(
                        teacher_code=teacher_code,
                        full_name=teacher_data['name'],
                        email=teacher_data['email'],
                        password=random_password,
                        phone=teacher_data.get('phone'),
                        birth_date=teacher_data.get('date_of_birth'),
                        hometown=teacher_data.get('hometown'),
                        faculty_id=faculty.id,
                        department_id=department_id
                    )
                    
                    teacher = await self._get_teacher_service().create_teacher_with_auth(teacher_create)
                    
                    if not teacher:
                        errors.append({
                            "row": index + 2,
                            "field": "general",
                            "error": "Failed to create teacher",
                            "value": None
                        })
                        continue
                    
                    # Store user data with password for Excel response
                    teacher_passwords.append({
                        "Họ tên": teacher_data['name'],
                        "Email": teacher_data['email'],
                        "Mật khẩu": random_password,
                        "Số điện thoại": teacher_data.get('phone', ''),
                        "Địa chỉ": teacher_data.get('address', ''),
                        "Ngày sinh": teacher_data.get('date_of_birth', ''),
                        "Quê quán": teacher_data.get('hometown', ''),
                        "Khoa": teacher_data['faculty_name'],
                        "Bộ môn": teacher_data.get('department_name', '')
                    })
                    
                    created_users.append({
                        "id": getattr(teacher, 'id', 'unknown'),
                        "full_name": getattr(teacher, 'full_name', teacher_data['name']),
                        "email": getattr(teacher, 'email', teacher_data['email']),
                        "faculty": teacher_data['faculty_name']
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing teacher row {index + 2}: {str(e)}")
                    errors.append({
                        "row": index + 2,
                        "field": "general",
                        "error": str(e),
                        "value": None
                    })
            
            # Generate Excel file with passwords for successful imports
            excel_buffer = None
            if teacher_passwords:
                excel_buffer = self._generate_excel_with_passwords(teacher_passwords, 'teachers')
            
            return BulkImportResult(
                total_rows=len(df),
                successful=len(created_users),
                failed=len(errors),
                errors=errors,
                created_users=created_users
            ), excel_buffer
            
        except Exception as e:
            logger.error(f"Error processing teacher Excel file: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

    async def process_student_excel(self, file: UploadFile) -> BulkImportResult:
        """Process Excel file for bulk student creation."""
        try:
            # Read Excel file
            content = await file.read()
            df = pd.read_excel(BytesIO(content))
            
            # Validate required columns
            required_columns = ['Họ tên', 'Email', 'Mã sinh viên', 'Lớp', 'Khoa', 'Ngành', 'Khóa']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required columns: {', '.join(missing_columns)}"
                )
            
            # Process each row
            results = []
            errors = []
            created_users = []
            student_passwords = []  # Store passwords for Excel response
            
            for index, row in df.iterrows():
                try:
                    # Validate and convert data
                    student_data = await self._validate_student_row(row, index + 2)  # +2 for header row
                    
                    # Look up faculty by name
                    faculty = await self.academic_repo.get_faculty_by_name(student_data['faculty_name'])
                    if not faculty:
                        errors.append({
                            "row": index + 2,
                            "field": "Khoa",
                            "error": f"Faculty '{student_data['faculty_name']}' not found",
                            "value": student_data['faculty_name']
                        })
                        continue
                    
                    # Look up major by name
                    major = await self.academic_repo.get_major_by_name(student_data['major_name'])
                    if not major:
                        errors.append({
                            "row": index + 2,
                            "field": "Ngành",
                            "error": f"Major '{student_data['major_name']}' not found",
                            "value": student_data['major_name']
                        })
                        continue
                    
                    # Look up cohort by name
                    cohort = await self.academic_repo.get_cohort_by_name(student_data['cohort_name'])
                    if not cohort:
                        errors.append({
                            "row": index + 2,
                            "field": "Khóa",
                            "error": f"Cohort '{student_data['cohort_name']}' not found",
                            "value": student_data['cohort_name']
                        })
                        continue
                    
                    # Generate random password
                    random_password = self._generate_random_password()
                    
                    # Create student
                    student_create = StudentCreate(
                        faculty_id=faculty.id,
                        major_id=major.id,
                        cohort_id=cohort.id,
                        full_name=student_data['name'],
                        email=student_data['email'],
                        password=random_password,
                        student_code=student_data['student_code'],
                        phone=student_data.get('phone'),
                        birth_date=student_data.get('date_of_birth'),
                        hometown=student_data.get('hometown'),
                        class_name=student_data['class_name']
                    )
                    
                    student = await self._get_student_service().create_student_with_auth(student_create)
                    
                    # Store user data with password for Excel response
                    student_passwords.append({
                        "Họ tên": student_data['name'],
                        "Email": student_data['email'],
                        "Mật khẩu": random_password,
                        "Mã sinh viên": student_data['student_code'],
                        "Số điện thoại": student_data.get('phone', ''),
                        "Địa chỉ": student_data.get('address', ''),
                        "Ngày sinh": student_data.get('date_of_birth', ''),
                        "Quê quán": student_data.get('hometown', ''),
                        "Lớp": student_data['class_name'],
                        "Khoa": student_data['faculty_name'],
                        "Ngành": student_data['major_name'],
                        "Khóa": student_data['cohort_name']
                    })
                    
                    created_users.append({
                        "id": student.id,
                        "full_name": student.full_name,
                        "email": student.email,
                        "student_code": student.student_code,
                        "class_name": student.class_name
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing student row {index + 2}: {str(e)}")
                    errors.append({
                        "row": index + 2,
                        "field": "general",
                        "error": str(e),
                        "value": None
                    })
            
            # Generate Excel file with passwords for successful imports
            excel_buffer = None
            if student_passwords:
                excel_buffer = self._generate_excel_with_passwords(student_passwords, 'students')
            
            return BulkImportResult(
                total_rows=len(df),
                successful=len(created_users),
                failed=len(errors),
                errors=errors,
                created_users=created_users
            ), excel_buffer
            
        except Exception as e:
            logger.error(f"Error processing student Excel file: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

    async def _validate_teacher_row(self, row: pd.Series, row_number: int) -> Dict[str, Any]:
        """Validate and convert teacher row data."""
        data = {}
        
        # Required fields
        if pd.isna(row.get('Họ tên')) or not str(row['Họ tên']).strip():
            raise ValueError("Name is required")
        data['name'] = str(row['Họ tên']).strip()
        
        if pd.isna(row.get('Email')) or not str(row['Email']).strip():
            raise ValueError("Email is required")
        data['email'] = str(row['Email']).strip()
        
        if pd.isna(row.get('Khoa')) or not str(row['Khoa']).strip():
            raise ValueError("Faculty is required")
        data['faculty_name'] = str(row['Khoa']).strip()
        
        # Optional department field
        if not pd.isna(row.get('Bộ môn')):
            data['department_name'] = str(row['Bộ môn']).strip()
        
        # Optional fields
        if not pd.isna(row.get('Số điện thoại')):
            data['phone'] = str(row['Số điện thoại']).strip()
        
        if not pd.isna(row.get('Địa chỉ')):
            data['address'] = str(row['Địa chỉ']).strip()
        
        if not pd.isna(row.get('Quê quán')):
            data['hometown'] = str(row['Quê quán']).strip()
        
        # Date of birth
        if not pd.isna(row.get('Ngày sinh')):
            try:
                if isinstance(row['Ngày sinh'], str):
                    data['date_of_birth'] = datetime.strptime(row['Ngày sinh'], '%Y-%m-%d').date()
                else:
                    data['date_of_birth'] = row['Ngày sinh'].date()
            except (ValueError, AttributeError):
                raise ValueError("Invalid date format for date of birth. Use YYYY-MM-DD")
        
        return data

    async def _validate_student_row(self, row: pd.Series, row_number: int) -> Dict[str, Any]:
        """Validate and convert student row data."""
        data = {}
        
        # Required fields
        if pd.isna(row.get('Họ tên')) or not str(row['Họ tên']).strip():
            raise ValueError("Name is required")
        data['name'] = str(row['Họ tên']).strip()
        
        if pd.isna(row.get('Email')) or not str(row['Email']).strip():
            raise ValueError("Email is required")
        data['email'] = str(row['Email']).strip()
        
        if pd.isna(row.get('Mã sinh viên')) or not str(row['Mã sinh viên']).strip():
            raise ValueError("Student code is required")
        data['student_code'] = str(row['Mã sinh viên']).strip()
        
        if pd.isna(row.get('Lớp')) or not str(row['Lớp']).strip():
            raise ValueError("Class is required")
        data['class_name'] = str(row['Lớp']).strip()
        
        # Required academic fields
        if pd.isna(row.get('Khoa')) or not str(row['Khoa']).strip():
            raise ValueError("Faculty is required")
        data['faculty_name'] = str(row['Khoa']).strip()
        
        if pd.isna(row.get('Ngành')) or not str(row['Ngành']).strip():
            raise ValueError("Major is required")
        data['major_name'] = str(row['Ngành']).strip()
        
        if pd.isna(row.get('Khóa')) or not str(row['Khóa']).strip():
            raise ValueError("Cohort is required")
        data['cohort_name'] = str(row['Khóa']).strip()
        
        # Optional fields
        if not pd.isna(row.get('Số điện thoại')):
            data['phone'] = str(row['Số điện thoại']).strip()
        
        if not pd.isna(row.get('Địa chỉ')):
            data['address'] = str(row['Địa chỉ']).strip()
        
        if not pd.isna(row.get('Quê quán')):
            data['hometown'] = str(row['Quê quán']).strip()
        
        # Date of birth
        if not pd.isna(row.get('Ngày sinh')):
            try:
                if isinstance(row['Ngày sinh'], str):
                    data['date_of_birth'] = datetime.strptime(row['Ngày sinh'], '%Y-%m-%d').date()
                else:
                    data['date_of_birth'] = row['Ngày sinh'].date()
            except (ValueError, AttributeError):
                raise ValueError("Invalid date format for date of birth. Use YYYY-MM-DD")
        
        return data

    def _generate_excel_with_passwords(self, user_data: List[Dict], user_type: str) -> BytesIO:
        """Generate Excel file with user data including passwords."""
        df = pd.DataFrame(user_data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = 'Giảng viên' if user_type == 'teachers' else 'Sinh viên'
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output
