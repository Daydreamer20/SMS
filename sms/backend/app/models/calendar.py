"""
Calendar model definitions for events and calendar integrations.
"""

from datetime import datetime, time
from enum import Enum
from typing import List, Optional
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EventType(str, Enum):
    """Enumeration for event types."""
    ACADEMIC = "academic"
    EXAM = "exam"
    HOLIDAY = "holiday"
    MEETING = "meeting"
    ACTIVITY = "activity"
    OTHER = "other"


class RecurrenceType(str, Enum):
    """Enumeration for event recurrence types."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class CalendarEvent(Base):
    """Calendar Event model."""

    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), default=EventType.OTHER.value)
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    recurrence_type: Mapped[str] = mapped_column(String(50), default=RecurrenceType.NONE.value)
    recurrence_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key relationships
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    class_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    creator = relationship("User", backref="created_events")
    class_ = relationship("Class", backref="events")
    attendees = relationship("EventAttendee", back_populates="event")
    
    def __repr__(self) -> str:
        """String representation of CalendarEvent."""
        return f"<CalendarEvent {self.title}>"


class EventAttendee(Base):
    """Event Attendee model."""

    __tablename__ = "event_attendees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("calendar_events.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    attendance_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, accepted, declined
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("CalendarEvent", back_populates="attendees")
    user = relationship("User", backref="event_attendances")
    
    def __repr__(self) -> str:
        """String representation of EventAttendee."""
        return f"<EventAttendee {self.id}>"


class CalendarIntegration(Base):
    """Calendar Integration model for external calendar services."""

    __tablename__ = "calendar_integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50))  # google, outlook, etc.
    access_token: Mapped[str] = mapped_column(String(1024))
    refresh_token: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    token_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    calendar_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="calendar_integrations")
    
    def __repr__(self) -> str:
        """String representation of CalendarIntegration."""
        return f"<CalendarIntegration {self.provider} for {self.user_id}>" 