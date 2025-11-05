from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from supabase import Client
from app.core.database import get_supabase
from app.schemas import (
    FacultyCreate, FacultyUpdate, FacultyResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    MajorCreate, MajorUpdate, MajorResponse,
    SubjectCreate, SubjectUpdate, SubjectResponse,
    AcademicYearCreate, AcademicYearUpdate, AcademicYearResponse,
    CohortCreate, CohortUpdate, CohortResponse,
    SemesterCreate, SemesterUpdate, SemesterResponse,
    StudyPhaseCreate, StudyPhaseUpdate, StudyPhaseResponse,
    BaseResponse, PaginatedResponse
)
from app.services import (
    FacultyService, DepartmentService, MajorService,
    SubjectService, AcademicYearService, CohortService,
    SemesterService, StudyPhaseService
)

router = APIRouter(prefix="/academic", tags=["Academic"])


# Faculty endpoints
@router.post("/faculties", response_model=BaseResponse)
async def create_faculty(
    faculty_data: FacultyCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new faculty."""
    try:
        faculty_service = FacultyService(supabase)
        faculty = await faculty_service.create(faculty_data.model_dump())
        
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create faculty"
            )
        
        return BaseResponse(
            message="Faculty created successfully",
            data={"id": faculty.id, "name": faculty.name, "code": faculty.code}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create faculty error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/faculties", response_model=PaginatedResponse)
async def get_faculties(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    supabase: Client = Depends(get_supabase)
):
    """Get all faculties with pagination."""
    try:
        faculty_service = FacultyService(supabase)
        result = await faculty_service.get_all(page, limit)
        
        return PaginatedResponse(
            items=[faculty.model_dump() for faculty in result["items"]],
            total=result["total"],
            page=result["page"],
            limit=result["limit"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        print(f"Get faculties error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/faculties/{faculty_id}", response_model=FacultyResponse)
async def get_faculty(
    faculty_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get faculty by ID."""
    try:
        faculty_service = FacultyService(supabase)
        faculty = await faculty_service.get_by_id(faculty_id)
        
        if not faculty:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
        
        return FacultyResponse(**faculty.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get faculty error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/faculties/{faculty_id}", response_model=BaseResponse)
async def update_faculty(
    faculty_id: int,
    faculty_data: FacultyUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update faculty by ID."""
    try:
        faculty_service = FacultyService(supabase)
        faculty = await faculty_service.update(faculty_id, faculty_data.model_dump(exclude_none=True))
        
        if not faculty:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
        
        return BaseResponse(message="Faculty updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update faculty error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/faculties/{faculty_id}", response_model=BaseResponse)
async def delete_faculty(
    faculty_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete faculty by ID."""
    try:
        faculty_service = FacultyService(supabase)
        success = await faculty_service.delete(faculty_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty not found")
        
        return BaseResponse(message="Faculty deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete faculty error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Department endpoints
@router.post("/departments", response_model=BaseResponse)
async def create_department(
    department_data: DepartmentCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new department."""
    try:
        department_service = DepartmentService(supabase)
        department = await department_service.create(department_data.model_dump())
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create department"
            )
        
        return BaseResponse(
            message="Department created successfully",
            data={"id": department.id, "name": department.name, "code": department.code}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create department error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/departments", response_model=PaginatedResponse)
async def get_departments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    faculty_id: int = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all departments with pagination and optional faculty filter."""
    try:
        department_service = DepartmentService(supabase)
        
        if faculty_id:
            departments = await department_service.get_by_faculty(faculty_id)
            return PaginatedResponse(
                items=[dept.model_dump() for dept in departments],
                total=len(departments),
                page=1,
                limit=len(departments),
                total_pages=1
            )
        else:
            result = await department_service.get_all(page, limit)
            return PaginatedResponse(
                items=[dept.model_dump() for dept in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get departments error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get department by ID."""
    try:
        department_service = DepartmentService(supabase)
        department = await department_service.get_by_id(department_id)
        
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        
        return DepartmentResponse(**department.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get department error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/departments/{department_id}", response_model=BaseResponse)
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update department by ID."""
    try:
        department_service = DepartmentService(supabase)
        department = await department_service.update(department_id, department_data.model_dump(exclude_unset=True))
        
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        
        return BaseResponse(
            message="Department updated successfully",
            data={"id": department.id, "name": department.name, "code": department.code}
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Update department error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/departments/{department_id}", response_model=BaseResponse)
async def delete_department(
    department_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete department by ID."""
    try:
        department_service = DepartmentService(supabase)
        success = await department_service.delete(department_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        
        return BaseResponse(message="Department deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete department error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Similar patterns for Major, Subject, AcademicYear, and Cohort endpoints

# Major endpoints
@router.post("/majors", response_model=BaseResponse)
async def create_major(
    major_data: MajorCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new major."""
    try:
        major_service = MajorService(supabase)
        major = await major_service.create(major_data.model_dump())
        
        if not major:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create major"
            )
        
        return BaseResponse(
            message="Major created successfully",
            data={"id": major.id, "name": major.name, "code": major.code}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create major error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/majors", response_model=PaginatedResponse)
async def get_majors(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    faculty_id: int = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all majors with pagination and optional faculty filter."""
    try:
        major_service = MajorService(supabase)
        
        if faculty_id:
            majors = await major_service.get_by_faculty(faculty_id)
            return PaginatedResponse(
                items=[major.model_dump() for major in majors],
                total=len(majors),
                page=1,
                limit=len(majors),
                total_pages=1
            )
        else:
            result = await major_service.get_all(page, limit)
            return PaginatedResponse(
                items=[major.model_dump() for major in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get majors error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/majors/{major_id}", response_model=MajorResponse)
async def get_major(
    major_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get major by ID."""
    try:
        major_service = MajorService(supabase)
        major = await major_service.get_by_id(major_id)
        
        if not major:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Major not found")
        
        return MajorResponse(**major.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get major error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/majors/{major_id}", response_model=BaseResponse)
async def update_major(
    major_id: int,
    major_data: MajorUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update major by ID."""
    try:
        major_service = MajorService(supabase)
        major = await major_service.update(major_id, major_data.model_dump(exclude_none=True))
        
        if not major:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Major not found")
        
        return BaseResponse(message="Major updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update major error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/majors/{major_id}", response_model=BaseResponse)
async def delete_major(
    major_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete major by ID."""
    try:
        major_service = MajorService(supabase)
        success = await major_service.delete(major_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Major not found")
        
        return BaseResponse(message="Major deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete major error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Subject endpoints
@router.post("/subjects", response_model=BaseResponse)
async def create_subject(
    subject_data: SubjectCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new subject."""
    try:
        subject_service = SubjectService(supabase)
        subject = await subject_service.create(subject_data.model_dump())
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create subject"
            )
        
        return BaseResponse(
            message="Subject created successfully",
            data={"id": subject.id, "name": subject.name, "code": subject.code, "credits": subject.credits}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create subject error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/subjects", response_model=PaginatedResponse)
async def get_subjects(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    department_id: int = Query(None),
    faculty_id: int = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all subjects with pagination and optional department/faculty filters."""
    try:
        subject_service = SubjectService(supabase)
        
        if faculty_id:
            # Filter by faculty (through department relationship)
            subjects = await subject_service.get_by_faculty(faculty_id)
            return PaginatedResponse(
                items=[subj.model_dump() for subj in subjects],
                total=len(subjects),
                page=1,
                limit=len(subjects),
                total_pages=1
            )
        elif department_id:
            # Filter by department
            subjects = await subject_service.get_by_department(department_id)
            return PaginatedResponse(
                items=[subj.model_dump() for subj in subjects],
                total=len(subjects),
                page=1,
                limit=len(subjects),
                total_pages=1
            )
        else:
            # Get all subjects with pagination
            result = await subject_service.get_all(page, limit)
            return PaginatedResponse(
                items=[subj.model_dump() for subj in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get subjects error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get subject by ID."""
    try:
        subject_service = SubjectService(supabase)
        subject = await subject_service.get_by_id(subject_id)
        
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        
        return SubjectResponse(**subject.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get subject error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/subjects/{subject_id}", response_model=BaseResponse)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update subject by ID."""
    try:
        subject_service = SubjectService(supabase)
        subject = await subject_service.update(subject_id, subject_data.model_dump(exclude_none=True))
        
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        
        return BaseResponse(message="Subject updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update subject error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/subjects/{subject_id}", response_model=BaseResponse)
async def delete_subject(
    subject_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete subject by ID."""
    try:
        subject_service = SubjectService(supabase)
        success = await subject_service.delete(subject_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        
        return BaseResponse(message="Subject deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete subject error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Academic Year endpoints
@router.post("/academic-years", response_model=BaseResponse)
async def create_academic_year(
    academic_year_data: AcademicYearCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new academic year."""
    try:
        academic_year_service = AcademicYearService(supabase)
        academic_year = await academic_year_service.create(academic_year_data.model_dump())
        
        if not academic_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create academic year"
            )
        
        return BaseResponse(
            message="Academic year created successfully",
            data={"id": academic_year.id, "name": academic_year.name}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create academic year error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/academic-years", response_model=PaginatedResponse)
async def get_academic_years(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    supabase: Client = Depends(get_supabase)
):
    """Get all academic years with pagination."""
    try:
        academic_year_service = AcademicYearService(supabase)
        result = await academic_year_service.get_all(page, limit)
        
        return PaginatedResponse(
            items=[ay.model_dump() for ay in result["items"]],
            total=result["total"],
            page=result["page"],
            limit=result["limit"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        print(f"Get academic years error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/academic-years/{academic_year_id}", response_model=AcademicYearResponse)
async def get_academic_year(
    academic_year_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get academic year by ID."""
    try:
        academic_year_service = AcademicYearService(supabase)
        academic_year = await academic_year_service.get_by_id(academic_year_id)
        
        if not academic_year:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic year not found")
        
        return AcademicYearResponse(**academic_year.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get academic year error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/academic-years/current", response_model=AcademicYearResponse)
async def get_current_academic_year(supabase: Client = Depends(get_supabase)):
    """Get current academic year."""
    try:
        academic_year_service = AcademicYearService(supabase)
        academic_year = await academic_year_service.get_current_academic_year()
        
        if not academic_year:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No current academic year found")
        
        return AcademicYearResponse(**academic_year.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current academic year error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/academic-years/{academic_year_id}", response_model=BaseResponse)
async def update_academic_year(
    academic_year_id: int,
    academic_year_data: AcademicYearUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update academic year by ID."""
    try:
        academic_year_service = AcademicYearService(supabase)
        academic_year = await academic_year_service.update(academic_year_id, academic_year_data.model_dump(exclude_none=True))
        
        if not academic_year:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic year not found")
        
        return BaseResponse(message="Academic year updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update academic year error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/academic-years/{academic_year_id}", response_model=BaseResponse)
async def delete_academic_year(
    academic_year_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete academic year by ID."""
    try:
        academic_year_service = AcademicYearService(supabase)
        success = await academic_year_service.delete(academic_year_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic year not found")
        
        return BaseResponse(message="Academic year deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete academic year error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Cohort endpoints
@router.post("/cohorts", response_model=BaseResponse)
async def create_cohort(
    cohort_data: CohortCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new cohort."""
    try:
        cohort_service = CohortService(supabase)
        cohort = await cohort_service.create(cohort_data.model_dump())
        
        if not cohort:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create cohort"
            )
        
        return BaseResponse(
            message="Cohort created successfully",
            data={"id": cohort.id, "name": cohort.name}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create cohort error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/cohorts", response_model=PaginatedResponse)
async def get_cohorts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    start_year: int = Query(None),
    end_year: int = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all cohorts with pagination and optional year range filter."""
    try:
        cohort_service = CohortService(supabase)
        
        if start_year and end_year:
            cohorts = await cohort_service.get_by_year_range(start_year, end_year)
            return PaginatedResponse(
                items=[cohort.model_dump() for cohort in cohorts],
                total=len(cohorts),
                page=1,
                limit=len(cohorts),
                total_pages=1
            )
        else:
            result = await cohort_service.get_all(page, limit)
            return PaginatedResponse(
                items=[cohort.model_dump() for cohort in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get cohorts error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/cohorts/{cohort_id}", response_model=CohortResponse)
async def get_cohort(
    cohort_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get cohort by ID."""
    try:
        cohort_service = CohortService(supabase)
        cohort = await cohort_service.get_by_id(cohort_id)
        
        if not cohort:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohort not found")
        
        return CohortResponse(**cohort.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get cohort error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/cohorts/{cohort_id}", response_model=BaseResponse)
async def update_cohort(
    cohort_id: int,
    cohort_data: CohortUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update cohort by ID."""
    try:
        cohort_service = CohortService(supabase)
        cohort = await cohort_service.update(cohort_id, cohort_data.model_dump(exclude_none=True))
        
        if not cohort:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohort not found")
        
        return BaseResponse(message="Cohort updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update cohort error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/cohorts/{cohort_id}", response_model=BaseResponse)
async def delete_cohort(
    cohort_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete cohort by ID."""
    try:
        cohort_service = CohortService(supabase)
        success = await cohort_service.delete(cohort_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohort not found")
        
        return BaseResponse(message="Cohort deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete cohort error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Semester endpoints
@router.post("/semesters", response_model=BaseResponse)
async def create_semester(
    semester_data: SemesterCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new semester."""
    try:
        semester_service = SemesterService(supabase)
        semester = await semester_service.create(semester_data.model_dump())
        
        if not semester:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create semester"
            )
        
        return BaseResponse(
            message="Semester created successfully",
            data={"id": semester.id, "name": semester.name}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create semester error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/semesters", response_model=PaginatedResponse)
async def get_semesters(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    academic_year_id: int = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all semesters with pagination and optional academic year filter."""
    try:
        semester_service = SemesterService(supabase)
        
        if academic_year_id:
            semesters = await semester_service.get_by_academic_year(academic_year_id)
            return PaginatedResponse(
                items=[semester.model_dump() for semester in semesters],
                total=len(semesters),
                page=1,
                limit=len(semesters),
                total_pages=1
            )
        else:
            result = await semester_service.get_all(page, limit)
            return PaginatedResponse(
                items=[semester.model_dump() for semester in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get semesters error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/semesters/{semester_id}", response_model=SemesterResponse)
async def get_semester(
    semester_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get semester by ID."""
    try:
        semester_service = SemesterService(supabase)
        semester = await semester_service.get_by_id(semester_id)
        
        if not semester:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")
        
        return SemesterResponse(**semester.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get semester error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/semesters/current", response_model=SemesterResponse)
async def get_current_semester(supabase: Client = Depends(get_supabase)):
    """Get current semester."""
    try:
        semester_service = SemesterService(supabase)
        semester = await semester_service.get_current_semester()
        
        if not semester:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No current semester found")
        
        return SemesterResponse(**semester.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current semester error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/semesters/{semester_id}", response_model=BaseResponse)
async def update_semester(
    semester_id: int,
    semester_data: SemesterUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update semester by ID."""
    try:
        semester_service = SemesterService(supabase)
        semester = await semester_service.update(semester_id, semester_data.model_dump(exclude_none=True))
        
        if not semester:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")
        
        return BaseResponse(message="Semester updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update semester error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/semesters/{semester_id}", response_model=BaseResponse)
async def delete_semester(
    semester_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete semester by ID."""
    try:
        semester_service = SemesterService(supabase)
        success = await semester_service.delete(semester_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")
        
        return BaseResponse(message="Semester deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete semester error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Study Phase endpoints
@router.post("/study-phases", response_model=BaseResponse)
async def create_study_phase(
    study_phase_data: StudyPhaseCreate,
    supabase: Client = Depends(get_supabase)
):
    """Create a new study phase."""
    try:
        study_phase_service = StudyPhaseService(supabase)
        study_phase = await study_phase_service.create(study_phase_data.model_dump())
        
        if not study_phase:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create study phase"
            )
        
        return BaseResponse(
            message="Study phase created successfully",
            data={"id": study_phase.id, "name": study_phase.name}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Create study phase error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/study-phases", response_model=PaginatedResponse)
async def get_study_phases(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    semester_id: int = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all study phases with pagination and optional semester filter."""
    try:
        study_phase_service = StudyPhaseService(supabase)
        
        if semester_id:
            study_phases = await study_phase_service.get_by_semester(semester_id)
            return PaginatedResponse(
                items=[sp.model_dump() for sp in study_phases],
                total=len(study_phases),
                page=1,
                limit=len(study_phases),
                total_pages=1
            )
        else:
            result = await study_phase_service.get_all(page, limit)
            return PaginatedResponse(
                items=[sp.model_dump() for sp in result["items"]],
                total=result["total"],
                page=result["page"],
                limit=result["limit"],
                total_pages=result["total_pages"]
            )
    except Exception as e:
        print(f"Get study phases error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/study-phases/{study_phase_id}", response_model=StudyPhaseResponse)
async def get_study_phase(
    study_phase_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Get study phase by ID."""
    try:
        study_phase_service = StudyPhaseService(supabase)
        study_phase = await study_phase_service.get_by_id(study_phase_id)
        
        if not study_phase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study phase not found")
        
        return StudyPhaseResponse(**study_phase.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get study phase error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/study-phases/current", response_model=StudyPhaseResponse)
async def get_current_study_phase(supabase: Client = Depends(get_supabase)):
    """Get current study phase."""
    try:
        study_phase_service = StudyPhaseService(supabase)
        study_phase = await study_phase_service.get_current_study_phase()
        
        if not study_phase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No current study phase found")
        
        return StudyPhaseResponse(**study_phase.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current study phase error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/study-phases/{study_phase_id}", response_model=BaseResponse)
async def update_study_phase(
    study_phase_id: int,
    study_phase_data: StudyPhaseUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Update study phase by ID."""
    try:
        study_phase_service = StudyPhaseService(supabase)
        study_phase = await study_phase_service.update(study_phase_id, study_phase_data.model_dump(exclude_none=True))
        
        if not study_phase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study phase not found")
        
        return BaseResponse(message="Study phase updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update study phase error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/study-phases/{study_phase_id}", response_model=BaseResponse)
async def delete_study_phase(
    study_phase_id: int,
    supabase: Client = Depends(get_supabase)
):
    """Delete study phase by ID."""
    try:
        study_phase_service = StudyPhaseService(supabase)
        success = await study_phase_service.delete(study_phase_id)
        
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study phase not found")
        
        return BaseResponse(message="Study phase deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete study phase error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
