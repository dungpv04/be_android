from typing import Optional, List, Dict, Any
from supabase import Client
from app.models import Faculty, Department, Major, Subject, AcademicYear, Cohort, Semester, StudyPhase
from app.repositories import (
    FacultyRepository, DepartmentRepository, MajorRepository,
    SubjectRepository, AcademicYearRepository, CohortRepository
)
from app.services.base import BaseService


class FacultyService(BaseService[Faculty]):
    """Service for Faculty business logic."""
    
    def __init__(self, supabase: Client):
        repository = FacultyRepository(supabase)
        super().__init__(repository)
    
    async def get_by_code(self, code: str) -> Optional[Faculty]:
        """Get faculty by code."""
        return await self.repository.get_by_code(code)
    
    async def create(self, data: Dict[str, Any]) -> Optional[Faculty]:
        """Create faculty with validation."""
        # Check if code is unique
        existing = await self.repository.get_by_code(data.get("code"))
        if existing:
            raise ValueError("Faculty code already exists")
        
        return await self.repository.create(data)


class DepartmentService(BaseService[Department]):
    """Service for Department business logic."""
    
    def __init__(self, supabase: Client):
        repository = DepartmentRepository(supabase)
        super().__init__(repository)
    
    async def get_by_code(self, code: str) -> Optional[Department]:
        """Get department by code."""
        return await self.repository.get_by_code(code)
    
    async def get_by_faculty(self, faculty_id: int) -> List[Department]:
        """Get departments by faculty."""
        return await self.repository.get_by_faculty(faculty_id)
    
    async def create(self, data: Dict[str, Any]) -> Optional[Department]:
        """Create department with validation."""
        # Check if code is unique
        existing = await self.repository.get_by_code(data.get("code"))
        if existing:
            raise ValueError("Department code already exists")
        
        return await self.repository.create(data)


class MajorService(BaseService[Major]):
    """Service for Major business logic."""
    
    def __init__(self, supabase: Client):
        repository = MajorRepository(supabase)
        super().__init__(repository)
    
    async def get_by_code(self, code: str) -> Optional[Major]:
        """Get major by code."""
        return await self.repository.get_by_code(code)
    
    async def get_by_faculty(self, faculty_id: int) -> List[Major]:
        """Get majors by faculty."""
        return await self.repository.get_by_faculty(faculty_id)
    
    async def create(self, data: Dict[str, Any]) -> Optional[Major]:
        """Create major with validation."""
        # Check if code is unique
        existing = await self.repository.get_by_code(data.get("code"))
        if existing:
            raise ValueError("Major code already exists")
        
        return await self.repository.create(data)


class SubjectService(BaseService[Subject]):
    """Service for Subject business logic."""
    
    def __init__(self, supabase: Client):
        repository = SubjectRepository(supabase)
        super().__init__(repository)
    
    async def get_by_code(self, code: str) -> Optional[Subject]:
        """Get subject by code."""
        return await self.repository.get_by_code(code)
    
    async def get_by_department(self, department_id: int) -> List[Subject]:
        """Get subjects by department."""
        return await self.repository.get_by_department(department_id)
    
    async def create(self, data: Dict[str, Any]) -> Optional[Subject]:
        """Create subject with validation."""
        # Check if code is unique
        existing = await self.repository.get_by_code(data.get("code"))
        if existing:
            raise ValueError("Subject code already exists")
        
        return await self.repository.create(data)


class AcademicYearService(BaseService[AcademicYear]):
    """Service for Academic Year business logic."""
    
    def __init__(self, supabase: Client):
        repository = AcademicYearRepository(supabase)
        super().__init__(repository)
    
    async def get_current_academic_year(self) -> Optional[AcademicYear]:
        """Get current academic year."""
        return await self.repository.get_current_academic_year()
    
    async def create(self, data: Dict[str, Any]) -> Optional[AcademicYear]:
        """Create academic year with validation."""
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if start_date and end_date and start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        return await self.repository.create(data)


class CohortService(BaseService[Cohort]):
    """Service for Cohort business logic."""
    
    def __init__(self, supabase: Client):
        repository = CohortRepository(supabase)
        super().__init__(repository)
    
    async def get_by_year_range(self, start_year: int, end_year: int) -> List[Cohort]:
        """Get cohorts by year range."""
        return await self.repository.get_by_year_range(start_year, end_year)
    
    async def create(self, data: Dict[str, Any]) -> Optional[Cohort]:
        """Create cohort with validation."""
        start_year = data.get("start_year")
        end_year = data.get("end_year")
        
        if start_year and end_year and start_year >= end_year:
            raise ValueError("Start year must be before end year")
        
        return await self.repository.create(data)


class SemesterService(BaseService):
    """Service for Semester operations."""
    
    def __init__(self, supabase: Client):
        from app.repositories import SemesterRepository
        self.repository = SemesterRepository(supabase)
    
    async def get_by_academic_year(self, academic_year_id: int) -> List[Semester]:
        """Get semesters by academic year."""
        return await self.repository.get_by_academic_year(academic_year_id)
    
    async def get_current_semester(self) -> Optional[Semester]:
        """Get current semester."""
        return await self.repository.get_current_semester()
    
    async def create(self, data: Dict[str, Any]) -> Optional[Semester]:
        """Create semester with validation."""
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if start_date and end_date and start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        return await self.repository.create(data)


class StudyPhaseService(BaseService):
    """Service for StudyPhase operations."""
    
    def __init__(self, supabase: Client):
        from app.repositories import StudyPhaseRepository
        self.repository = StudyPhaseRepository(supabase)
    
    async def get_by_semester(self, semester_id: int) -> List[StudyPhase]:
        """Get study phases by semester."""
        return await self.repository.get_by_semester(semester_id)
    
    async def get_current_study_phase(self) -> Optional[StudyPhase]:
        """Get current study phase."""
        return await self.repository.get_current_study_phase()
    
    async def create(self, data: Dict[str, Any]) -> Optional[StudyPhase]:
        """Create study phase with validation."""
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if start_date and end_date and start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        return await self.repository.create(data)
