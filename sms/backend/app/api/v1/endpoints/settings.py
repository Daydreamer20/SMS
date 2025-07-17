"""
API endpoints for school settings.
"""

from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app import schemas
from app.api.v1 import deps
from app.models import User, SchoolSettings, SystemSettings, GradingSystem

router = APIRouter()


# School Settings Endpoints
@router.get("/school", response_model=schemas.SchoolSettings)
async def get_school_settings(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve school settings.
    """
    result = await db.execute(select(SchoolSettings).limit(1))
    settings = result.scalars().first()
    
    if not settings:
        raise HTTPException(
            status_code=404, detail="School settings not found"
        )
    return settings


@router.post("/school", response_model=schemas.SchoolSettings)
async def create_school_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    settings_in: schemas.SchoolSettingsCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create school settings.
    """
    # Check if settings already exist
    result = await db.execute(select(SchoolSettings))
    existing_settings = result.scalars().first()
    
    if existing_settings:
        raise HTTPException(
            status_code=400, detail="School settings already exist. Use PUT method to update."
        )
    
    settings = SchoolSettings(**settings_in.dict())
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings


@router.put("/school", response_model=schemas.SchoolSettings)
async def update_school_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    settings_in: schemas.SchoolSettingsUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update school settings.
    """
    result = await db.execute(select(SchoolSettings).limit(1))
    settings = result.scalars().first()
    
    if not settings:
        raise HTTPException(
            status_code=404, detail="School settings not found"
        )
    
    update_data = settings_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    return settings


# System Settings Endpoints
@router.get("/system", response_model=List[schemas.SystemSettings])
async def get_system_settings(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all system settings.
    """
    result = await db.execute(select(SystemSettings))
    settings = result.scalars().all()
    return settings


@router.get("/system/public", response_model=List[schemas.SystemSettings])
async def get_public_system_settings(
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Retrieve public system settings.
    """
    result = await db.execute(select(SystemSettings).where(SystemSettings.is_public == True))
    settings = result.scalars().all()
    return settings


@router.post("/system", response_model=schemas.SystemSettings)
async def create_system_setting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    setting_in: schemas.SystemSettingsCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a system setting.
    """
    # Check if setting with the same key exists
    result = await db.execute(select(SystemSettings).where(SystemSettings.key == setting_in.key))
    existing_setting = result.scalars().first()
    
    if existing_setting:
        raise HTTPException(
            status_code=400, detail=f"Setting with key '{setting_in.key}' already exists"
        )
    
    setting = SystemSettings(**setting_in.dict())
    db.add(setting)
    await db.commit()
    await db.refresh(setting)
    return setting


@router.get("/system/{key}", response_model=schemas.SystemSettings)
async def get_system_setting_by_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    key: str = Path(...),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get a system setting by key.
    """
    result = await db.execute(select(SystemSettings).where(SystemSettings.key == key))
    setting = result.scalars().first()
    
    if not setting:
        raise HTTPException(
            status_code=404, detail=f"Setting with key '{key}' not found"
        )
    return setting


@router.put("/system/{key}", response_model=schemas.SystemSettings)
async def update_system_setting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    key: str = Path(...),
    setting_in: schemas.SystemSettingsUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a system setting by key.
    """
    result = await db.execute(select(SystemSettings).where(SystemSettings.key == key))
    setting = result.scalars().first()
    
    if not setting:
        raise HTTPException(
            status_code=404, detail=f"Setting with key '{key}' not found"
        )
    
    update_data = setting_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)
    
    await db.commit()
    await db.refresh(setting)
    return setting


@router.delete("/system/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_setting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    key: str = Path(...),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a system setting by key.
    """
    result = await db.execute(select(SystemSettings).where(SystemSettings.key == key))
    setting = result.scalars().first()
    
    if not setting:
        raise HTTPException(
            status_code=404, detail=f"Setting with key '{key}' not found"
        )
    
    await db.delete(setting)
    await db.commit()
    return None


# Grading System Endpoints
@router.get("/grading", response_model=List[schemas.GradingSystem])
async def get_grading_systems(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all grading systems.
    """
    result = await db.execute(select(GradingSystem))
    grading_systems = result.scalars().all()
    return grading_systems


@router.post("/grading", response_model=schemas.GradingSystem)
async def create_grading_system(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grading_system_in: schemas.GradingSystemCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a grading system.
    """
    # Check if a grading system with the same name exists
    result = await db.execute(select(GradingSystem).where(GradingSystem.name == grading_system_in.name))
    existing_system = result.scalars().first()
    
    if existing_system:
        raise HTTPException(
            status_code=400, detail=f"Grading system with name '{grading_system_in.name}' already exists"
        )
    
    # If this is set as active, deactivate all other grading systems
    if grading_system_in.is_active:
        result = await db.execute(select(GradingSystem).where(GradingSystem.is_active == True))
        active_systems = result.scalars().all()
        for system in active_systems:
            system.is_active = False
    
    grading_system = GradingSystem(**grading_system_in.dict())
    db.add(grading_system)
    await db.commit()
    await db.refresh(grading_system)
    return grading_system


@router.get("/grading/{grading_system_id}", response_model=schemas.GradingSystem)
async def get_grading_system(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grading_system_id: int = Path(...),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get a grading system by ID.
    """
    result = await db.execute(select(GradingSystem).where(GradingSystem.id == grading_system_id))
    grading_system = result.scalars().first()
    
    if not grading_system:
        raise HTTPException(
            status_code=404, detail=f"Grading system with ID {grading_system_id} not found"
        )
    return grading_system


@router.put("/grading/{grading_system_id}", response_model=schemas.GradingSystem)
async def update_grading_system(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grading_system_id: int = Path(...),
    grading_system_in: schemas.GradingSystemUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a grading system.
    """
    result = await db.execute(select(GradingSystem).where(GradingSystem.id == grading_system_id))
    grading_system = result.scalars().first()
    
    if not grading_system:
        raise HTTPException(
            status_code=404, detail=f"Grading system with ID {grading_system_id} not found"
        )
    
    # If updating to active, deactivate all other grading systems
    if grading_system_in.is_active:
        result = await db.execute(
            select(GradingSystem).where(
                GradingSystem.is_active == True,
                GradingSystem.id != grading_system_id
            )
        )
        active_systems = result.scalars().all()
        for system in active_systems:
            system.is_active = False
    
    update_data = grading_system_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grading_system, field, value)
    
    await db.commit()
    await db.refresh(grading_system)
    return grading_system


@router.delete("/grading/{grading_system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grading_system(
    *,
    db: AsyncSession = Depends(deps.get_db),
    grading_system_id: int = Path(...),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a grading system.
    """
    result = await db.execute(select(GradingSystem).where(GradingSystem.id == grading_system_id))
    grading_system = result.scalars().first()
    
    if not grading_system:
        raise HTTPException(
            status_code=404, detail=f"Grading system with ID {grading_system_id} not found"
        )
    
    await db.delete(grading_system)
    await db.commit()
    return None 