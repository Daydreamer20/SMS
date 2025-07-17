"""
Email notification model definitions.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmailStatus(str, Enum):
    """Enumeration for email status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class EmailType(str, Enum):
    """Enumeration for email types."""
    GENERAL = "general"
    ANNOUNCEMENT = "announcement"
    HOMEWORK = "homework"
    EXAM = "exam"
    EVENT = "event"
    REPORT = "report"
    ATTENDANCE = "attendance"
    FEE = "fee"
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    VERIFICATION = "verification"


class EmailTemplate(Base):
    """Email template model."""

    __tablename__ = "email_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    email_type: Mapped[str] = mapped_column(String(50), default=EmailType.GENERAL.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    emails: Mapped[List["EmailNotification"]] = relationship("EmailNotification", back_populates="template")
    
    def __repr__(self) -> str:
        """String representation of EmailTemplate."""
        return f"<EmailTemplate {self.name}>"


class EmailNotification(Base):
    """Email notification model."""

    __tablename__ = "email_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    recipient_email: Mapped[str] = mapped_column(String(255))
    recipient_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=EmailStatus.PENDING.value)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("email_templates.id", ondelete="SET NULL"), nullable=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    template: Mapped[Optional[EmailTemplate]] = relationship("EmailTemplate", back_populates="emails")
    sender = relationship("User", backref="sent_emails")
    
    def __repr__(self) -> str:
        """String representation of EmailNotification."""
        return f"<EmailNotification {self.id}: {self.subject}>"


class EmailSettings(Base):
    """Email settings model."""

    __tablename__ = "email_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    smtp_server: Mapped[str] = mapped_column(String(255))
    smtp_port: Mapped[int] = mapped_column(Integer)
    smtp_username: Mapped[str] = mapped_column(String(255))
    smtp_password: Mapped[str] = mapped_column(String(255))
    use_tls: Mapped[bool] = mapped_column(Boolean, default=True)
    sender_email: Mapped[str] = mapped_column(String(255))
    sender_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        """String representation of EmailSettings."""
        return f"<EmailSettings {self.sender_email}>"


class EmailSubscription(Base):
    """Email subscription preferences for users."""

    __tablename__ = "email_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    general_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    announcement_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    homework_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    exam_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    event_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    report_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    attendance_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    fee_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    user = relationship("User", backref="email_subscription")
    
    def __repr__(self) -> str:
        """String representation of EmailSubscription."""
        return f"<EmailSubscription for user {self.user_id}>" 