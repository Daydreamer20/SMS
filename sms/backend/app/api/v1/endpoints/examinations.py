"""
API endpoints for examinations and grading.
"""

from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app import schemas
from app.api.v1 import deps
from app.models import User, Examination, ExaminationSubject, Grade, GradingScale
from app.models import ExaminationType, GradeStatus

router = APIRouter()


@router.get("/", response_model=List[schemas.Examination])
async def get_examinations(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    is_published: Optional[bool] = None,
) -> Any:
    """
    Retrieve examinations.
    """
    query = select(Examination).offset(skip).limit(limit)
    
    if class_id:
        query = query.where(Examination.class_id == class_id)
    if academic_year_id:
        query = query.where(Examination.academic_year_id == academic_year_id)
    if is_published is not None:
        query = query.where(Examination.is_published == is_published)
    
    result = await db.execute(query)
    examinations = result.scalars().all()
    return examinations


@router.post("/", response_model=schemas.Examination)
async def create_examination(
    *,
    db: AsyncSession = Depends(deps.get_db),
    examination_in: schemas.ExaminationCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new examination.
    """
    examination = Examination(
        name=examination_in.name,
        exam_type=examination_in.exam_type,
        start_date=examination_in.start_date,
        end_date=examination_in.end_date,
        description=examination_in.description,
        class_id=examination_in.class_id,
        academic_year_id=examination_in.academic_year_id,
        is_published=examination_in.is_published,
    )
    db.add(examination)
    await db.commit()
    await db.refresh(examination)
    return examination


@router.get("/{examination_id}", response_model=schemas.Examination)
async def get_examination(
    *,
    db: AsyncSession = Depends(deps.get_db),
    examination_id: int = Path(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get examination by ID.
    """
    result = await db.execute(
        select(Examination).where(Examination.id == examination_id)
    )
    examination = result.scalars().first()
    
    if not examination:
        raise HTTPException(
            status_code=404, detail="Examination not found"
        )
    return examination


@router.put("/{examination_id}", response_model=schemas.Examination)
async def update_examination(
    *,
    db: AsyncSession = Depends(deps.get_db),
    examination_id: int = Path(...),
    examination_in: schemas.ExaminationUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update examination.
    """
    result = await db.execute(
        select(Examination).where(Examination.id == examination_id)
    )
    examination = result.scalars().first()
    
    if not examination:
        raise HTTPException(
            status_code=404, detail="Examination not found"
        )
    
    update_data = examination_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(examination, field, value)
    
    await db.commit()
    await db.refresh(examination)
    return examination


@router.delete("/{examination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_examination(
    *,
    db: AsyncSession = Depends(deps.get_db),
    examination_id: int = Path(...),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete examination.
    """
    result = await db.execute(
        select(Examination).where(Examination.id == examination_id)
    )
    examination = result.scalars().first()
    
    if not examination:
        raise HTTPException(
            status_code=404, detail="Examination not found"
        )
    
    await db.delete(examination)
    await db.commit()
    return None


# Examination Subject Endpoints

@router.post("/{examination_id}/subjects", response_model=schemas.ExaminationSubject)
async def add_subject_to_examination(
    *,
    db: AsyncSession = Depends(deps.get_db),
    examination_id: int = Path(...),
    subject_in: schemas.ExaminationSubjectCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Add a subject to an examination.
    """
    # Verify examination exists
    result = await db.execute(
        select(Examination).where(Examination.id == examination_id)
    )
    examination = result.scalars().first()
    
    if not examination:
        raise HTTPException(
            status_code=404, detail="Examination not found"
        )
    
    # Create examination subject
    examination_subject = ExaminationSubject(
        examination_id=examination_id,
        subject_id=subject_in.subject_id,
        exam_date=subject_in.exam_date,
        total_marks=subject_in.total_marks,
        passing_marks=subject_in.passing_marks,
    )
    
    db.add(examination_subject)
    await db.commit()
    await db.refresh(examination_subject)
    return examination_subject


@router.get("/{examination_id}/subjects", response_model=List[schemas.ExaminationSubjectWithDetails])
async def get_examination_subjects(
    *,
    db: AsyncSession = Depends(deps.get_db),
    examination_id: int = Path(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all subjects for an examination.
    """
    # Use selectinload to load the related subject and examination
    result = await db.execute(
        select(ExaminationSubject)
        .where(ExaminationSubject.examination_id == examination_id)
        .options(
            selectinload(ExaminationSubject.subject),
            selectinload(ExaminationSubject.examination)
        )
    )
    examination_subjects = result.scalars().all()
    return examination_subjects


# Grade Endpoints

@router.post("/subjects/{examination_subject_id}/grades", response_model=schemas.Grade)
async def create_grade(
    *,
    db: AsyncSession = Depends(deps.get_db),
    examination_subject_id: int = Path(...),
    grade_in: schemas.GradeCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new grade for a student's examination subject.
    """
    # Verify examination subject exists
    result = await db.execute(
        select(ExaminationSubject).where(ExaminationSubject.id == examination_subject_id)
    )
    examination_subject = result.scalars().first()
    
    if not examination_subject:
        raise HTTPException(
            status_code=404, detail="Examination subject not found"
        )
    
    # Check if grade already exists for this student and examination subject
    result = await db.execute(
        select(Grade)
        .where(
            Grade.student_id == grade_in.student_id,
            Grade.examination_subject_id == examination_subject_id
        )
    )
    existing_grade = result.scalars().first()
    
    if existing_grade:
        raise HTTPException(
            status_code=400, detail="Grade already exists for this student and examination subject"
        )
    
    # Create grade
    grade = Grade(
        student_id=grade_in.student_id,
        examination_subject_id=examination_subject_id,
        marks_obtained=grade_in.marks_obtained,
        grade_letter=grade_in.grade_letter,
        remarks=grade_in.remarks,
        status=grade_in.status,
    )
    
    db.add(grade)
    await db.commit()
    await db.refresh(grade)
    return grade


@router.get("/subjects/{examination_subject_id}/grades", response_model=List[schemas.Grade])
async def get_grades_by_examination_subject(
    *,
    db: AsyncSession = Depends(deps.get_db),
    examination_subject_id: int = Path(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all grades for an examination subject.
    """
    result = await db.execute(
        select(Grade).where(Grade.examination_subject_id == examination_subject_id)
    )
    grades = result.scalars().all()
    return grades


@router.get("/grades/{grade_id}", response_model=schemas.GradeWithDetails)
async def get_grade(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grade_id: int = Path(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get grade by ID with examination subject details.
    """
    result = await db.execute(
        select(Grade)
        .where(Grade.id == grade_id)
        .options(selectinload(Grade.examination_subject))
    )
    grade = result.scalars().first()
    
    if not grade:
        raise HTTPException(
            status_code=404, detail="Grade not found"
        )
    return grade


@router.put("/grades/{grade_id}", response_model=schemas.Grade)
async def update_grade(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grade_id: int = Path(...),
    grade_in: schemas.GradeUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update grade.
    """
    result = await db.execute(
        select(Grade).where(Grade.id == grade_id)
    )
    grade = result.scalars().first()
    
    if not grade:
        raise HTTPException(
            status_code=404, detail="Grade not found"
        )
    
    update_data = grade_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grade, field, value)
    
    await db.commit()
    await db.refresh(grade)
    return grade


# Grading Scale Endpoints

@router.get("/grading-scales", response_model=List[schemas.GradingScale])
async def get_grading_scales(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve grading scales.
    """
    result = await db.execute(
        select(GradingScale).offset(skip).limit(limit)
    )
    grading_scales = result.scalars().all()
    return grading_scales


@router.post("/grading-scales", response_model=schemas.GradingScale)
async def create_grading_scale(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grading_scale_in: schemas.GradingScaleCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new grading scale.
    """
    grading_scale = GradingScale(
        letter=grading_scale_in.letter,
        min_marks=grading_scale_in.min_marks,
        max_marks=grading_scale_in.max_marks,
        gpa=grading_scale_in.gpa,
        description=grading_scale_in.description,
    )
    db.add(grading_scale)
    await db.commit()
    await db.refresh(grading_scale)
    return grading_scale


@router.put("/grading-scales/{grading_scale_id}", response_model=schemas.GradingScale)
async def update_grading_scale(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grading_scale_id: int = Path(...),
    grading_scale_in: schemas.GradingScaleUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update grading scale.
    """
    result = await db.execute(
        select(GradingScale).where(GradingScale.id == grading_scale_id)
    )
    grading_scale = result.scalars().first()
    
    if not grading_scale:
        raise HTTPException(
            status_code=404, detail="Grading scale not found"
        )
    
    update_data = grading_scale_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grading_scale, field, value)
    
    await db.commit()
    await db.refresh(grading_scale)
    return grading_scale


@router.delete("/grading-scales/{grading_scale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grading_scale(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grading_scale_id: int = Path(...),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete grading scale.
    """
    result = await db.execute(
        select(GradingScale).where(GradingScale.id == grading_scale_id)
    )
    grading_scale = result.scalars().first()
    
    if not grading_scale:
        raise HTTPException(
            status_code=404, detail="Grading scale not found"
        )
    
    await db.delete(grading_scale)
    await db.commit()
    return None 