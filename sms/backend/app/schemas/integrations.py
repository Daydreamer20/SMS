"""
Pydantic schemas for external integration-related models.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, validator

from app.models.integrations import IntegrationType, LogLevel


class ExternalApplicationBase(BaseModel):
    """Base schema for External Application model."""
    
    name: str
    description: Optional[str] = None
    integration_type: str = IntegrationType.API.value
    base_url: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    config: Optional[Dict[str, Any]] = None


class ExternalApplicationCreate(ExternalApplicationBase):
    """Schema for creating a new external application."""
    pass


class ExternalApplicationUpdate(BaseModel):
    """Schema for updating an external application."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    integration_type: Optional[str] = None
    base_url: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class ExternalApplication(ExternalApplicationBase):
    """Schema for retrieving an external application."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class APIKeyBase(BaseModel):
    """Base schema for API Key model."""
    
    key_name: str
    api_key: str
    expires_at: Optional[datetime] = None
    is_active: bool = True


class APIKeyCreate(BaseModel):
    """Schema for creating a new API key."""
    
    key_name: str
    api_key: str
    expires_at: Optional[datetime] = None
    is_active: bool = True


class APIKeyUpdate(BaseModel):
    """Schema for updating an API key."""
    
    key_name: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class APIKey(APIKeyBase):
    """Schema for retrieving an API key."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    application_id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime


class WebhookEndpointBase(BaseModel):
    """Base schema for Webhook Endpoint model."""
    
    name: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    is_active: bool = True


class WebhookEndpointCreate(WebhookEndpointBase):
    """Schema for creating a new webhook endpoint."""
    pass


class WebhookEndpointUpdate(BaseModel):
    """Schema for updating a webhook endpoint."""
    
    name: Optional[str] = None
    url: Optional[str] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None


class WebhookEndpoint(WebhookEndpointBase):
    """Schema for retrieving a webhook endpoint."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    application_id: int
    created_at: datetime
    updated_at: datetime


class IntegrationLogBase(BaseModel):
    """Base schema for Integration Log model."""
    
    event: str
    level: str = LogLevel.INFO.value
    message: str
    details: Optional[Dict[str, Any]] = None
    success: bool = True


class IntegrationLogCreate(IntegrationLogBase):
    """Schema for creating a new integration log."""
    pass


class IntegrationLog(IntegrationLogBase):
    """Schema for retrieving an integration log."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    application_id: int
    created_at: datetime 