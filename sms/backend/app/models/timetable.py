"""
Timetable model definitions.
"""

from datetime import datetime, time
from enum import Enum
from typing import List, Optional
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DayOfWeek(str, Enum):
    """Enumeration for days of the week."""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Period(Base):
    """Time Period model for defining standard periods in a day."""

    __tablename__ = "periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))  # e.g., "Period 1", "Break", "Lunch"
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    is_break: Mapped[bool] = mapped_column(Boolean, default=False)
    academic_year: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    timetable_entries: Mapped[List["TimetableEntry"]] = relationship("TimetableEntry", back_populates="period")
    
    def __repr__(self) -> str:
        """String representation of Period."""
        return f"<Period {self.name} {self.start_time}-{self.end_time}>"


class Timetable(Base):
    """Timetable model for organizing class schedules."""

    __tablename__ = "timetables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    academic_year: Mapped[str] = mapped_column(String(20))
    term: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_from: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    
    # Relationships
    class_ = relationship("Class", backref="timetables")
    entries: Mapped[List["TimetableEntry"]] = relationship("TimetableEntry", back_populates="timetable")
    
    def __repr__(self) -> str:
        """String representation of Timetable."""
        return f"<Timetable {self.name} for class {self.class_id}>"


class TimetableEntry(Base):
    """Timetable Entry model for individual schedule items."""

    __tablename__ = "timetable_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    day_of_week: Mapped[str] = mapped_column(String(20))
    room: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    timetable_id: Mapped[int] = mapped_column(Integer, ForeignKey("timetables.id", ondelete="CASCADE"))
    period_id: Mapped[int] = mapped_column(Integer, ForeignKey("periods.id", ondelete="CASCADE"))
    subject_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    teacher_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    timetable: Mapped[Timetable] = relationship("Timetable", back_populates="entries")
    period: Mapped[Period] = relationship("Period", back_populates="timetable_entries")
    subject = relationship("Subject", backref="timetable_entries")
    teacher = relationship("Staff", backref="timetable_entries")
    
    def __repr__(self) -> str:
        """String representation of TimetableEntry."""
        return f"<TimetableEntry {self.day_of_week} {self.period_id} {self.subject_id or 'No subject'}>" 