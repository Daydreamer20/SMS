"""
External integration model definitions.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IntegrationType(str, Enum):
    """Enumeration for integration types."""
    API = "api"
    WEBHOOK = "webhook"
    OAUTH = "oauth"
    DATA_IMPORT = "data_import"
    DATA_EXPORT = "data_export"
    LMS = "lms"
    PAYMENT = "payment"
    COMMUNICATION = "communication"
    OTHER = "other"


class LogLevel(str, Enum):
    """Enumeration for log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ExternalApplication(Base):
    """External Application model for third-party integrations."""

    __tablename__ = "external_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    integration_type: Mapped[str] = mapped_column(String(50), default=IntegrationType.API.value)
    base_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="application")
    webhook_endpoints: Mapped[List["WebhookEndpoint"]] = relationship("WebhookEndpoint", back_populates="application")
    logs: Mapped[List["IntegrationLog"]] = relationship("IntegrationLog", back_populates="application")
    
    def __repr__(self) -> str:
        """String representation of ExternalApplication."""
        return f"<ExternalApplication {self.name}>"


class APIKey(Base):
    """API Key model for managing access to the API."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key_name: Mapped[str] = mapped_column(String(100))
    api_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("external_applications.id", ondelete="CASCADE"))
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    application: Mapped[ExternalApplication] = relationship("ExternalApplication", back_populates="api_keys")
    created_by = relationship("User", backref="created_api_keys")
    
    def __repr__(self) -> str:
        """String representation of APIKey."""
        return f"<APIKey {self.key_name}>"


class WebhookEndpoint(Base):
    """Webhook Endpoint model for managing outgoing webhooks."""

    __tablename__ = "webhook_endpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(255))
    events: Mapped[list] = mapped_column(JSON)  # List of events to trigger webhook
    secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key relationships
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("external_applications.id", ondelete="CASCADE"))
    
    # Relationships
    application: Mapped[ExternalApplication] = relationship("ExternalApplication", back_populates="webhook_endpoints")
    
    def __repr__(self) -> str:
        """String representation of WebhookEndpoint."""
        return f"<WebhookEndpoint {self.name}: {self.url}>"


class IntegrationLog(Base):
    """Integration Log model for tracking integration activities."""

    __tablename__ = "integration_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event: Mapped[str] = mapped_column(String(100))
    level: Mapped[str] = mapped_column(String(20), default=LogLevel.INFO.value)
    message: Mapped[str] = mapped_column(Text)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Foreign key relationships
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("external_applications.id", ondelete="CASCADE"))
    
    # Relationships
    application: Mapped[ExternalApplication] = relationship("ExternalApplication", back_populates="logs")
    
    def __repr__(self) -> str:
        """String representation of IntegrationLog."""
        return f"<IntegrationLog {self.event}: {self.level}>" 