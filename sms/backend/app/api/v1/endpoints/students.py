"""
Student management API endpoints.
"""

from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.deps import get_current_admin, get_current_teacher, get_current_student
from app.core.database import get_db
from app.models.student import Student, ParentGuardian
from app.models.user import User
from app.models.academic import StudentPerformanceReport, Class
from app.schemas.student import (
    Student as StudentSchema,
    StudentCreate,
    StudentUpdate,
    StudentWithClass,
    ParentGuardian as ParentGuardianSchema,
    ParentGuardianCreate,
    ParentGuardianUpdate,
)
from app.schemas.academic import (
    StudentPerformanceReport as StudentPerformanceReportSchema,
    StudentPerformanceReportCreate,
    StudentPerformanceReportUpdate,
    StudentPerformanceReportDetail,
)


router = APIRouter()


@router.get("/", response_model=List[StudentSchema])
async def read_students(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Retrieve students.
    """
    result = await db.execute(select(Student).offset(skip).limit(limit))
    students = result.scalars().all()
    return students


@router.post("/", response_model=StudentSchema)
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Create a new student.
    """
    # Check if user exists
    result = await db.execute(select(User).filter(User.id == student_in.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if student already exists for this user
    result = await db.execute(select(Student).filter(Student.user_id == student_in.user_id))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already exists for this user",
        )
    
    # Create new student
    student = Student(**student_in.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/me", response_model=StudentWithClass)
async def read_student_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> Any:
    """
    Get current student.
    """
    result = await db.execute(select(Student).filter(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found for current user",
        )
    return student


@router.get("/{student_id}", response_model=StudentWithClass)
async def read_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Get a specific student by id.
    """
    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student


@router.put("/{student_id}", response_model=StudentSchema)
async def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Update a student.
    """
    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    # Update student with input data
    update_data = student_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/{student_id}", response_model=StudentSchema)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete a student.
    """
    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    await db.delete(student)
    await db.commit()
    return student


# Parent/Guardian endpoints
@router.post("/parents", response_model=ParentGuardianSchema)
async def create_parent(
    parent_in: ParentGuardianCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Create a new parent/guardian.
    """
    parent = ParentGuardian(**parent_in.model_dump())
    db.add(parent)
    await db.commit()
    await db.refresh(parent)
    return parent


@router.get("/parents", response_model=List[ParentGuardianSchema])
async def read_parents(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Retrieve parents/guardians.
    """
    result = await db.execute(select(ParentGuardian).offset(skip).limit(limit))
    parents = result.scalars().all()
    return parents


@router.get("/parents/{parent_id}", response_model=ParentGuardianSchema)
async def read_parent(
    parent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Get a specific parent/guardian by id.
    """
    result = await db.execute(select(ParentGuardian).filter(ParentGuardian.id == parent_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent/Guardian not found",
        )
    return parent


@router.put("/parents/{parent_id}", response_model=ParentGuardianSchema)
async def update_parent(
    parent_id: int,
    parent_in: ParentGuardianUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Update a parent/guardian.
    """
    result = await db.execute(select(ParentGuardian).filter(ParentGuardian.id == parent_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent/Guardian not found",
        )
    
    # Update parent with input data
    update_data = parent_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(parent, field, value)
    
    await db.commit()
    await db.refresh(parent)
    return parent


@router.delete("/parents/{parent_id}", response_model=ParentGuardianSchema)
async def delete_parent(
    parent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete a parent/guardian.
    """
    result = await db.execute(select(ParentGuardian).filter(ParentGuardian.id == parent_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent/Guardian not found",
        )
    
    await db.delete(parent)
    await db.commit()
    return parent


@router.post("/{student_id}/link-parent/{parent_id}", response_model=StudentSchema)
async def link_parent_to_student(
    student_id: int,
    parent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Link a parent/guardian to a student.
    """
    # Check if student exists
    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    # Check if parent exists
    result = await db.execute(select(ParentGuardian).filter(ParentGuardian.id == parent_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent/Guardian not found",
        )
    
    # Link parent to student
    parent.students.append(student)
    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/{student_id}/unlink-parent/{parent_id}", response_model=StudentSchema)
async def unlink_parent_from_student(
    student_id: int,
    parent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Unlink a parent/guardian from a student.
    """
    # Check if student exists
    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    # Check if parent exists
    result = await db.execute(select(ParentGuardian).filter(ParentGuardian.id == parent_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent/Guardian not found",
        )
    
    # Unlink parent from student
    if student in parent.students:
        parent.students.remove(student)
        await db.commit()
        await db.refresh(student)
    
    return student


# Performance Report endpoints
@router.post("/performance-reports", response_model=StudentPerformanceReportSchema)
async def create_performance_report(
    report_in: StudentPerformanceReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Create a new student performance report.
    """
    # Check if student exists
    result = await db.execute(select(Student).filter(Student.id == report_in.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    # Check if class exists
    result = await db.execute(select(Class).filter(Class.id == report_in.class_id))
    class_ = result.scalar_one_or_none()
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found",
        )
    
    # Check if a report already exists for this student, term and academic year
    result = await db.execute(
        select(StudentPerformanceReport).filter(
            StudentPerformanceReport.student_id == report_in.student_id,
            StudentPerformanceReport.term == report_in.term,
            StudentPerformanceReport.academic_year == report_in.academic_year
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A performance report already exists for this student in this term and academic year",
        )
    
    # Create new performance report
    report = StudentPerformanceReport(**report_in.model_dump())
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/performance-reports", response_model=List[StudentPerformanceReportSchema])
async def read_performance_reports(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    term: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    class_id: Optional[int] = Query(None),
    is_published: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Retrieve student performance reports with optional filters.
    """
    query = select(StudentPerformanceReport)
    
    # Apply filters if provided
    if term:
        query = query.filter(StudentPerformanceReport.term == term)
    if academic_year:
        query = query.filter(StudentPerformanceReport.academic_year == academic_year)
    if class_id:
        query = query.filter(StudentPerformanceReport.class_id == class_id)
    if is_published is not None:
        query = query.filter(StudentPerformanceReport.is_published == is_published)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    return reports


@router.get("/performance-reports/me", response_model=List[StudentPerformanceReportSchema])
async def read_my_performance_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> Any:
    """
    Retrieve current student's performance reports.
    """
    # Get student ID for current user
    result = await db.execute(select(Student).filter(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found for current user",
        )
    
    # Get published reports for this student
    result = await db.execute(
        select(StudentPerformanceReport)
        .filter(
            StudentPerformanceReport.student_id == student.id,
            StudentPerformanceReport.is_published == True
        )
        .order_by(StudentPerformanceReport.academic_year.desc(), StudentPerformanceReport.term.desc())
    )
    reports = result.scalars().all()
    return reports


@router.get("/performance-reports/{report_id}", response_model=StudentPerformanceReportDetail)
async def read_performance_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Get a specific student performance report by id.
    """
    result = await db.execute(select(StudentPerformanceReport).filter(StudentPerformanceReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance report not found",
        )
    return report


@router.get("/performance-reports/student/{student_id}", response_model=List[StudentPerformanceReportSchema])
async def read_student_performance_reports(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    term: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Retrieve performance reports for a specific student.
    """
    # Check if student exists
    result = await db.execute(select(Student).filter(Student.id == student_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    # Build query
    query = select(StudentPerformanceReport).filter(StudentPerformanceReport.student_id == student_id)
    if term:
        query = query.filter(StudentPerformanceReport.term == term)
    if academic_year:
        query = query.filter(StudentPerformanceReport.academic_year == academic_year)
    
    # Order by academic year and term
    query = query.order_by(StudentPerformanceReport.academic_year.desc(), StudentPerformanceReport.term.desc())
    
    result = await db.execute(query)
    reports = result.scalars().all()
    return reports


@router.put("/performance-reports/{report_id}", response_model=StudentPerformanceReportSchema)
async def update_performance_report(
    report_id: int,
    report_in: StudentPerformanceReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Update a student performance report.
    """
    result = await db.execute(select(StudentPerformanceReport).filter(StudentPerformanceReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance report not found",
        )
    
    # Update report with input data
    update_data = report_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    await db.commit()
    await db.refresh(report)
    return report


@router.put("/performance-reports/{report_id}/publish", response_model=StudentPerformanceReportSchema)
async def publish_performance_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Publish a student performance report (admin only).
    """
    result = await db.execute(select(StudentPerformanceReport).filter(StudentPerformanceReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance report not found",
        )
    
    # Update report status
    report.is_published = True
    report.published_date = datetime.utcnow()
    
    await db.commit()
    await db.refresh(report)
    return report


@router.delete("/performance-reports/{report_id}", response_model=StudentPerformanceReportSchema)
async def delete_performance_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete a student performance report.
    """
    result = await db.execute(select(StudentPerformanceReport).filter(StudentPerformanceReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance report not found",
        )
    
    await db.delete(report)
    await db.commit()
    return report 