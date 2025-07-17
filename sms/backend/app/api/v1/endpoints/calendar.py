"""
Calendar API endpoints.
"""

from typing import Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.api.v1.deps import get_current_active_user, get_current_admin, get_db
from app.core.database import get_db
from app.models.user import User
from app.models.calendar import CalendarEvent, EventAttendee, CalendarIntegration
from app.schemas.calendar import (
    CalendarEvent as CalendarEventSchema,
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventWithAttendees,
    EventAttendee as EventAttendeeSchema,
    EventAttendeeCreate,
    EventAttendeeUpdate,
    CalendarIntegration as CalendarIntegrationSchema,
    CalendarIntegrationCreate,
    CalendarIntegrationUpdate
)

router = APIRouter()


@router.get("/", response_model=List[CalendarEventSchema])
async def read_calendar_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    is_public: Optional[bool] = None,
    class_id: Optional[int] = None,
) -> Any:
    """
    Retrieve calendar events.
    """
    query = select(CalendarEvent).offset(skip).limit(limit)
    
    # Apply filters if provided
    filters = []
    
    if start_date:
        filters.append(CalendarEvent.start_date >= start_date)
    
    if end_date:
        filters.append(or_(
            CalendarEvent.end_date <= end_date,
            and_(CalendarEvent.end_date.is_(None), CalendarEvent.start_date <= end_date)
        ))
    
    if event_type:
        filters.append(CalendarEvent.event_type == event_type)
    
    if is_public is not None:
        filters.append(CalendarEvent.is_public == is_public)
    
    if class_id:
        filters.append(CalendarEvent.class_id == class_id)
    
    # Non-admin users can only see their events or public events
    if not any(role.name == "admin" for role in current_user.roles):
        filters.append(or_(
            CalendarEvent.creator_id == current_user.id,
            CalendarEvent.is_public == True
        ))
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return events


@router.post("/", response_model=CalendarEventSchema, status_code=status.HTTP_201_CREATED)
async def create_calendar_event(
    *,
    db: AsyncSession = Depends(get_db),
    event_in: CalendarEventCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new calendar event.
    """
    event = CalendarEvent(
        **event_in.dict(),
        creator_id=current_user.id
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/{event_id}", response_model=CalendarEventWithAttendees)
async def read_calendar_event(
    *,
    db: AsyncSession = Depends(get_db),
    event_id: int = Path(..., title="The ID of the event to get"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get calendar event by ID with attendees.
    """
    event_query = select(CalendarEvent).where(CalendarEvent.id == event_id)
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    # Check if user has access to this event
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if not (is_admin or event.creator_id == current_user.id or event.is_public):
        raise HTTPException(status_code=403, detail="Not enough permissions to access this event")
    
    # Get event attendees
    attendees_query = select(EventAttendee).where(EventAttendee.event_id == event_id)
    attendees_result = await db.execute(attendees_query)
    attendees = attendees_result.scalars().all()
    
    return {**event.__dict__, "attendees": attendees}


@router.put("/{event_id}", response_model=CalendarEventSchema)
async def update_calendar_event(
    *,
    db: AsyncSession = Depends(get_db),
    event_id: int = Path(..., title="The ID of the event to update"),
    event_in: CalendarEventUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a calendar event.
    """
    event_query = select(CalendarEvent).where(CalendarEvent.id == event_id)
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    # Check if user has permission to update this event
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if not (is_admin or event.creator_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions to update this event")
    
    update_data = event_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_event(
    *,
    db: AsyncSession = Depends(get_db),
    event_id: int = Path(..., title="The ID of the event to delete"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a calendar event.
    """
    event_query = select(CalendarEvent).where(CalendarEvent.id == event_id)
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    # Check if user has permission to delete this event
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if not (is_admin or event.creator_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this event")
    
    await db.delete(event)
    await db.commit()
    
    return None


# Event Attendees endpoints

@router.post("/attendees", response_model=EventAttendeeSchema, status_code=status.HTTP_201_CREATED)
async def create_event_attendee(
    *,
    db: AsyncSession = Depends(get_db),
    attendee_in: EventAttendeeCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Add an attendee to a calendar event.
    """
    # Check if event exists
    event_query = select(CalendarEvent).where(CalendarEvent.id == attendee_in.event_id)
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    # Check if user has permission to add attendees
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if not (is_admin or event.creator_id == current_user.id):
        # Users can add themselves as attendees to public events
        if not (event.is_public and attendee_in.user_id == current_user.id):
            raise HTTPException(status_code=403, detail="Not enough permissions to add attendees to this event")
    
    # Check if attendee already exists
    existing_query = select(EventAttendee).where(
        (EventAttendee.event_id == attendee_in.event_id) &
        (EventAttendee.user_id == attendee_in.user_id)
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already an attendee of this event")
    
    attendee = EventAttendee(**attendee_in.dict())
    db.add(attendee)
    await db.commit()
    await db.refresh(attendee)
    return attendee


@router.put("/attendees/{attendee_id}", response_model=EventAttendeeSchema)
async def update_event_attendee(
    *,
    db: AsyncSession = Depends(get_db),
    attendee_id: int = Path(..., title="The ID of the attendee to update"),
    attendee_in: EventAttendeeUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an event attendee's status.
    """
    attendee_query = select(EventAttendee).where(EventAttendee.id == attendee_id)
    attendee_result = await db.execute(attendee_query)
    attendee = attendee_result.scalar_one_or_none()
    
    if not attendee:
        raise HTTPException(status_code=404, detail="Event attendee not found")
    
    # Users can update their own attendance status or if they are the event creator
    event_query = select(CalendarEvent).where(CalendarEvent.id == attendee.event_id)
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    is_admin = any(role.name == "admin" for role in current_user.roles)
    # Add null check before accessing creator_id
    if event is None:
        creator_id = None
    else:
        creator_id = event.creator_id

    if not (is_admin or attendee.user_id == current_user.id or creator_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions to update this attendance")
    
    update_data = attendee_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendee, field, value)
    
    await db.commit()
    await db.refresh(attendee)
    return attendee


@router.delete("/attendees/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_attendee(
    *,
    db: AsyncSession = Depends(get_db),
    attendee_id: int = Path(..., title="The ID of the attendee to delete"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Remove an attendee from a calendar event.
    """
    attendee_query = select(EventAttendee).where(EventAttendee.id == attendee_id)
    attendee_result = await db.execute(attendee_query)
    attendee = attendee_result.scalar_one_or_none()
    
    if not attendee:
        raise HTTPException(status_code=404, detail="Event attendee not found")
    
    # Users can remove themselves from events or if they are the event creator
    event_query = select(CalendarEvent).where(CalendarEvent.id == attendee.event_id)
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    is_admin = any(role.name == "admin" for role in current_user.roles)
    # Add null check before accessing creator_id
    if event is None:
        creator_id = None
    else:
        creator_id = event.creator_id

    if not (is_admin or attendee.user_id == current_user.id or creator_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions to remove this attendee")
    
    await db.delete(attendee)
    await db.commit()
    
    return None


# Calendar Integration endpoints

@router.get("/integrations", response_model=List[CalendarIntegrationSchema])
async def read_calendar_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve calendar integrations for the current user.
    """
    query = select(CalendarIntegration).where(CalendarIntegration.user_id == current_user.id)
    result = await db.execute(query)
    integrations = result.scalars().all()
    
    return integrations


@router.post("/integrations", response_model=CalendarIntegrationSchema, status_code=status.HTTP_201_CREATED)
async def create_calendar_integration(
    *,
    db: AsyncSession = Depends(get_db),
    integration_in: CalendarIntegrationCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new calendar integration for the current user.
    """
    # Check if integration with this provider already exists
    existing_query = select(CalendarIntegration).where(
        (CalendarIntegration.user_id == current_user.id) &
        (CalendarIntegration.provider == integration_in.provider)
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Integration with {integration_in.provider} already exists")
    
    integration = CalendarIntegration(
        **integration_in.dict(),
        user_id=current_user.id
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


@router.put("/integrations/{integration_id}", response_model=CalendarIntegrationSchema)
async def update_calendar_integration(
    *,
    db: AsyncSession = Depends(get_db),
    integration_id: int = Path(..., title="The ID of the integration to update"),
    integration_in: CalendarIntegrationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a calendar integration.
    """
    integration_query = select(CalendarIntegration).where(
        (CalendarIntegration.id == integration_id) &
        (CalendarIntegration.user_id == current_user.id)
    )
    integration_result = await db.execute(integration_query)
    integration = integration_result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Calendar integration not found")
    
    update_data = integration_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(integration, field, value)
    
    await db.commit()
    await db.refresh(integration)
    return integration


@router.delete("/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_integration(
    *,
    db: AsyncSession = Depends(get_db),
    integration_id: int = Path(..., title="The ID of the integration to delete"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a calendar integration.
    """
    integration_query = select(CalendarIntegration).where(
        (CalendarIntegration.id == integration_id) &
        (CalendarIntegration.user_id == current_user.id)
    )
    integration_result = await db.execute(integration_query)
    integration = integration_result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Calendar integration not found")
    
    await db.delete(integration)
    await db.commit()
    
    return None


@router.post("/integrations/{integration_id}/sync", response_model=CalendarIntegrationSchema)
async def sync_calendar(
    *,
    db: AsyncSession = Depends(get_db),
    integration_id: int = Path(..., title="The ID of the integration to sync"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Synchronize events with external calendar.
    This is a placeholder endpoint that will be implemented with actual sync logic.
    """
    integration_query = select(CalendarIntegration).where(
        (CalendarIntegration.id == integration_id) &
        (CalendarIntegration.user_id == current_user.id)
    )
    integration_result = await db.execute(integration_query)
    integration = integration_result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Calendar integration not found")
    
    # Placeholder for actual sync implementation
    # TODO: Implement calendar sync logic with external providers
    
    # Update the last sync timestamp
    integration.last_sync = datetime.utcnow()
    await db.commit()
    await db.refresh(integration)
    
    return integration 