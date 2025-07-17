"""
Fee management API endpoints.
"""

from typing import Any, List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.api.v1.deps import get_current_active_user, get_current_admin, get_db
from app.core.database import get_db
from app.models.user import User
from app.models.fees import FeeCategory, FeeStructure, FeeDueDate, FeeTransaction

router = APIRouter()


@router.get("/categories")
async def read_fee_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> Any:
    """
    Retrieve fee categories.
    """
    query = select(FeeCategory).offset(skip).limit(limit)
    
    if is_active is not None:
        query = query.where(FeeCategory.is_active == is_active)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return {"categories": categories}


@router.get("/structures")
async def read_fee_structures(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    class_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Any:
    """
    Retrieve fee structures.
    """
    query = select(FeeStructure).offset(skip).limit(limit)
    
    filters = []
    if category_id:
        filters.append(FeeStructure.category_id == category_id)
    if class_id:
        filters.append(FeeStructure.class_id == class_id)
    if academic_year:
        filters.append(FeeStructure.academic_year == academic_year)
    if is_active is not None:
        filters.append(FeeStructure.is_active == is_active)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    structures = result.scalars().all()
    
    return {"structures": structures}


@router.get("/transactions")
async def read_fee_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    fee_structure_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Any:
    """
    Retrieve fee transactions.
    """
    query = select(FeeTransaction).offset(skip).limit(limit)
    
    filters = []
    if student_id:
        filters.append(FeeTransaction.student_id == student_id)
    if fee_structure_id:
        filters.append(FeeTransaction.fee_structure_id == fee_structure_id)
    if payment_status:
        filters.append(FeeTransaction.payment_status == payment_status)
    if start_date:
        filters.append(FeeTransaction.transaction_date >= start_date)
    if end_date:
        filters.append(FeeTransaction.transaction_date <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return {"transactions": transactions} 