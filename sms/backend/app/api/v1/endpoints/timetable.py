"""
Timetable management API endpoints.
"""

from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.api.v1.deps import get_current_active_user, get_current_admin, get_db
from app.core.database import get_db
from app.models.user import User
from app.models.timetable import Period, Timetable, TimetableEntry

router = APIRouter()


@router.get("/periods")
async def read_periods(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    academic_year: Optional[str] = None,
) -> Any:
    """
    Retrieve time periods.
    """
    query = select(Period).offset(skip).limit(limit)
    
    filters = []
    if is_active is not None:
        filters.append(Period.is_active == is_active)
    if academic_year:
        filters.append(Period.academic_year == academic_year)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    periods = result.scalars().all()
    
    return {"periods": periods}


@router.get("/timetables")
async def read_timetables(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    class_id: Optional[int] = None,
    academic_year: Optional[str] = None,
) -> Any:
    """
    Retrieve timetables.
    """
    query = select(Timetable).offset(skip).limit(limit)
    
    filters = []
    if is_active is not None:
        filters.append(Timetable.is_active == is_active)
    if class_id:
        filters.append(Timetable.class_id == class_id)
    if academic_year:
        filters.append(Timetable.academic_year == academic_year)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    timetables = result.scalars().all()
    
    return {"timetables": timetables}


@router.get("/timetables/{timetable_id}/entries")
async def read_timetable_entries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    timetable_id: int = Path(..., title="The ID of the timetable"),
    skip: int = 0,
    limit: int = 100,
    day_of_week: Optional[str] = None,
) -> Any:
    """
    Retrieve entries for a specific timetable.
    """
    # Check if timetable exists
    timetable_result = await db.execute(select(Timetable).where(Timetable.id == timetable_id))
    timetable = timetable_result.scalar_one_or_none()
    
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    # Get timetable entries
    query = select(TimetableEntry).where(TimetableEntry.timetable_id == timetable_id)
    
    if day_of_week:
        query = query.where(TimetableEntry.day_of_week == day_of_week)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    entries = result.scalars().all()
    
    return {"entries": entries} 