"""
Settings models for school configuration.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import JSON, Column, DateTime, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SchoolSettings(Base):
    """School settings model."""

    __tablename__ = "school_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_name: Mapped[str] = mapped_column(String(255))
    school_address: Mapped[str] = mapped_column(String(500))
    school_email: Mapped[str] = mapped_column(String(100))
    school_phone: Mapped[str] = mapped_column(String(20))
    school_website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    school_logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    principal_name: Mapped[str] = mapped_column(String(100))
    established_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_academic_year_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        """String representation of SchoolSettings."""
        return f"<SchoolSettings {self.school_name}>"


class SystemSettings(Base):
    """System settings model for application configuration."""

    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[str] = mapped_column(String(500))
    value_type: Mapped[str] = mapped_column(String(20), default="string")  # string, number, boolean, json
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        """String representation of SystemSettings."""
        return f"<SystemSettings {self.key}>"


class GradingSystem(Base):
    """Grading system configuration model."""

    __tablename__ = "grading_systems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    grading_rules: Mapped[dict] = mapped_column(JSON)  # JSON field for storing grading rules
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        """String representation of GradingSystem."""
        return f"<GradingSystem {self.name}>" 