"""
Parent communication API endpoints.
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
from app.models.parent_communication import Message, MessageRecipient, Thread, ThreadMessage, ThreadParticipant, Announcement

router = APIRouter()


@router.get("/messages")
async def read_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve messages for the current user.
    """
    # Get messages where the current user is a recipient
    query = select(MessageRecipient).where(MessageRecipient.recipient_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    message_recipients = result.scalars().all()
    
    return {"messages": message_recipients}


@router.get("/threads")
async def read_threads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve threads for the current user.
    """
    # Get threads where the current user is a participant
    query = select(ThreadParticipant).where(ThreadParticipant.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    thread_participants = result.scalars().all()
    
    return {"threads": thread_participants}


@router.get("/announcements")
async def read_announcements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = True,
) -> Any:
    """
    Retrieve announcements.
    """
    query = select(Announcement).where(Announcement.is_active == is_active).offset(skip).limit(limit)
    result = await db.execute(query)
    announcements = result.scalars().all()
    
    return {"announcements": announcements} 