"""
Staff model definitions for teachers and other staff members.
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User

if TYPE_CHECKING:
    from app.models.academic import Class, Subject


class StaffType(str, Enum):
    """Enumeration for staff types."""
    TEACHER = "teacher"
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    ACCOUNTANT = "accountant"
    SUPPORT = "support"
    OTHER = "other"


class Staff(Base):
    """Staff model for school staff members."""

    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    staff_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    staff_type: Mapped[str] = mapped_column(String(50), default=StaffType.TEACHER.value)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    qualification: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_of_joining: Mapped[date] = mapped_column(Date, default=date.today)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped[User] = relationship("User", backref="staff")
    
    # Reverse relationships - these will be set up by the related models
    classes: Mapped[List["Class"]] = relationship(
        "Class", 
        primaryjoin="Staff.id==Class.teacher_id",
        back_populates="teacher"
    )
    subjects: Mapped[List["Subject"]] = relationship(
        "Subject", 
        primaryjoin="Staff.id==Subject.teacher_id",
        back_populates="teacher"
    )

    def __repr__(self) -> str:
        """String representation of Staff."""
        return f"<Staff {self.staff_id}>" 