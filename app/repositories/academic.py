from typing import Optional, List, Dict, Any
from supabase import Client
from app.models import Faculty, Department, Major, Subject, AcademicYear, Cohort, Semester, StudyPhase
from app.repositories.base import BaseRepository


class FacultyRepository(BaseRepository[Faculty]):
    """Repository for Faculty operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "faculties", Faculty)
    
    async def get_by_code(self, code: str) -> Optional[Faculty]:
        """Get faculty by code."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("code", code).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting faculty by code: {e}")
            return None


class DepartmentRepository(BaseRepository[Department]):
    """Repository for Department operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "departments", Department)
    
    async def get_by_faculty(self, faculty_id: int) -> List[Department]:
        """Get departments by faculty ID."""
        return await self.find_by_field("faculty_id", faculty_id)
    
    async def get_by_code(self, code: str) -> Optional[Department]:
        """Get department by code."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("code", code).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting department by code: {e}")
            return None


class MajorRepository(BaseRepository[Major]):
    """Repository for Major operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "majors", Major)
    
    async def get_by_faculty(self, faculty_id: int) -> List[Major]:
        """Get majors by faculty ID."""
        return await self.find_by_field("faculty_id", faculty_id)
    
    async def get_by_code(self, code: str) -> Optional[Major]:
        """Get major by code."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("code", code).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting major by code: {e}")
            return None


class SubjectRepository(BaseRepository[Subject]):
    """Repository for Subject operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "subjects", Subject)
    
    async def get_by_department(self, department_id: int) -> List[Subject]:
        """Get subjects by department ID."""
        return await self.find_by_field("department_id", department_id)
    
    async def get_by_code(self, code: str) -> Optional[Subject]:
        """Get subject by code."""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("code", code).execute()
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting subject by code: {e}")
            return None


class AcademicYearRepository(BaseRepository[AcademicYear]):
    """Repository for Academic Year operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "academic_years", AcademicYear)
    
    async def get_current_academic_year(self) -> Optional[AcademicYear]:
        """Get current academic year based on dates."""
        try:
            from datetime import date
            today = date.today()
            
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .lte("start_date", today.isoformat())
                       .gte("end_date", today.isoformat())
                       .execute())
            
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting current academic year: {e}")
            return None


class CohortRepository(BaseRepository[Cohort]):
    """Repository for Cohort operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "cohorts", Cohort)
    
    async def get_by_year_range(self, start_year: int, end_year: int) -> List[Cohort]:
        """Get cohorts by year range."""
        try:
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .gte("start_year", start_year)
                       .lte("end_year", end_year)
                       .execute())
            
            return [self.model_class(**item) for item in response.data] if response.data else []
        except Exception as e:
            print(f"Error getting cohorts by year range: {e}")
            return []


class SemesterRepository(BaseRepository[Semester]):
    """Repository for Semester operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "semesters", Semester)
    
    async def get_by_academic_year(self, academic_year_id: int) -> List[Semester]:
        """Get semesters by academic year ID."""
        return await self.find_by_field("academic_year_id", academic_year_id)
    
    async def get_current_semester(self) -> Optional[Semester]:
        """Get current semester based on dates."""
        try:
            from datetime import date
            today = date.today()
            
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .lte("start_date", today.isoformat())
                       .gte("end_date", today.isoformat())
                       .execute())
            
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting current semester: {e}")
            return None


class StudyPhaseRepository(BaseRepository[StudyPhase]):
    """Repository for StudyPhase operations."""
    
    def __init__(self, supabase: Client):
        super().__init__(supabase, "study_phases", StudyPhase)
    
    async def get_by_semester(self, semester_id: int) -> List[StudyPhase]:
        """Get study phases by semester ID."""
        return await self.find_by_field("semester_id", semester_id)
    
    async def get_current_study_phase(self) -> Optional[StudyPhase]:
        """Get current study phase based on dates."""
        try:
            from datetime import date
            today = date.today()
            
            response = (self.supabase.table(self.table_name)
                       .select("*")
                       .lte("start_date", today.isoformat())
                       .gte("end_date", today.isoformat())
                       .execute())
            
            if response.data:
                return self.model_class(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting current study phase: {e}")
            return None
