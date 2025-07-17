"""
Pydantic schemas for calendar-related models.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.calendar import EventType, RecurrenceType


class CalendarEventBase(BaseModel):
    """Base schema for Calendar Event model."""
    
    title: str
    description: Optional[str] = None
    event_type: str = EventType.OTHER.value
    start_date: datetime
    end_date: Optional[datetime] = None
    all_day: bool = False
    location: Optional[str] = None
    recurrence_type: str = RecurrenceType.NONE.value
    recurrence_end_date: Optional[datetime] = None
    is_public: bool = True
    class_id: Optional[int] = None


class CalendarEventCreate(CalendarEventBase):
    """Schema for creating a new calendar event."""
    pass


class CalendarEventUpdate(CalendarEventBase):
    """Schema for updating a calendar event."""
    title: Optional[str] = None
    start_date: Optional[datetime] = None


class CalendarEvent(CalendarEventBase):
    """Schema for retrieving a calendar event."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime


class EventAttendeeBase(BaseModel):
    """Base schema for Event Attendee model."""
    
    event_id: int
    user_id: int
    attendance_status: str = "pending"


class EventAttendeeCreate(EventAttendeeBase):
    """Schema for creating a new event attendee."""
    pass


class EventAttendeeUpdate(BaseModel):
    """Schema for updating an event attendee."""
    
    attendance_status: str


class EventAttendee(EventAttendeeBase):
    """Schema for retrieving an event attendee."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class CalendarIntegrationBase(BaseModel):
    """Base schema for Calendar Integration model."""
    
    provider: str
    calendar_id: Optional[str] = None
    is_active: bool = True


class CalendarIntegrationCreate(CalendarIntegrationBase):
    """Schema for creating a new calendar integration."""
    
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None


class CalendarIntegrationUpdate(BaseModel):
    """Schema for updating a calendar integration."""
    
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    calendar_id: Optional[str] = None
    is_active: Optional[bool] = None
    last_sync: Optional[datetime] = None


class CalendarIntegration(CalendarIntegrationBase):
    """Schema for retrieving a calendar integration."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CalendarEventWithAttendees(CalendarEvent):
    """Schema for calendar event with attendees."""
    
    attendees: List[EventAttendee] = [] 