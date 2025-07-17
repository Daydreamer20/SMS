"""
Staff management API endpoints.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.deps import get_current_admin, get_current_teacher
from app.core.database import get_db
from app.models.staff import Staff
from app.models.user import User, Role
from app.schemas.staff import (
    Staff as StaffSchema,
    StaffCreate,
    StaffUpdate,
    StaffWithUser,
    StaffWithClasses,
)


router = APIRouter()


@router.get("/", response_model=List[StaffSchema])
async def read_staff_members(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Retrieve staff members.
    """
    result = await db.execute(select(Staff).offset(skip).limit(limit))
    staff_members = result.scalars().all()
    return staff_members


@router.post("/", response_model=StaffSchema)
async def create_staff_member(
    staff_in: StaffCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Create a new staff member.
    """
    # Check if user exists
    result = await db.execute(select(User).filter(User.id == staff_in.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if staff member already exists for this user
    result = await db.execute(select(Staff).filter(Staff.user_id == staff_in.user_id))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff member already exists for this user",
        )
    
    # Create new staff member
    staff = Staff(**staff_in.model_dump())
    db.add(staff)
    await db.commit()
    await db.refresh(staff)
    
    # Add teacher role to user if staff type is teacher
    if staff.staff_type == "teacher":
        result = await db.execute(select(Role).filter(Role.name == "teacher"))
        teacher_role = result.scalar_one_or_none()
        
        if not teacher_role:
            teacher_role = Role(name="teacher", description="Teacher role")
            db.add(teacher_role)
            await db.commit()
            await db.refresh(teacher_role)
        
        # Check if user already has this role
        if teacher_role not in user.roles:
            user.roles.append(teacher_role)
            await db.commit()
    
    return staff


@router.get("/me", response_model=StaffWithUser)
async def read_staff_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
) -> Any:
    """
    Get current staff member.
    """
    result = await db.execute(select(Staff).filter(Staff.user_id == current_user.id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found for current user",
        )
    return staff


@router.get("/{staff_id}", response_model=StaffWithUser)
async def read_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Get a specific staff member by id.
    """
    result = await db.execute(select(Staff).filter(Staff.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found",
        )
    return staff


@router.get("/{staff_id}/classes", response_model=StaffWithClasses)
async def read_staff_with_classes(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Get a specific staff member with their classes and subjects.
    """
    result = await db.execute(select(Staff).filter(Staff.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found",
        )
    return staff


@router.put("/{staff_id}", response_model=StaffSchema)
async def update_staff(
    staff_id: int,
    staff_in: StaffUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Update a staff member.
    """
    result = await db.execute(select(Staff).filter(Staff.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found",
        )
    
    # Update staff with input data
    update_data = staff_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(staff, field, value)
    
    await db.commit()
    await db.refresh(staff)
    return staff


@router.delete("/{staff_id}", response_model=StaffSchema)
async def delete_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete a staff member.
    """
    result = await db.execute(select(Staff).filter(Staff.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found",
        )
    
    await db.delete(staff)
    await db.commit()
    return staff 