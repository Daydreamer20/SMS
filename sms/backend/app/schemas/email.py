"""
Pydantic schemas for email notification-related models.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.email import EmailStatus, EmailType


class EmailTemplateBase(BaseModel):
    """Base schema for Email Template model."""
    
    name: str
    subject: str
    body: str
    email_type: str = EmailType.GENERAL.value
    is_active: bool = True


class EmailTemplateCreate(EmailTemplateBase):
    """Schema for creating a new email template."""
    pass


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an email template."""
    
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    email_type: Optional[str] = None
    is_active: Optional[bool] = None


class EmailTemplate(EmailTemplateBase):
    """Schema for retrieving an email template."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class EmailNotificationBase(BaseModel):
    """Base schema for Email Notification model."""
    
    subject: str
    body: str
    recipient_email: EmailStr
    recipient_name: Optional[str] = None
    template_id: Optional[int] = None


class EmailNotificationCreate(EmailNotificationBase):
    """Schema for creating a new email notification."""
    pass


class EmailNotificationUpdate(BaseModel):
    """Schema for updating an email notification."""
    
    status: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None


class EmailNotification(EmailNotificationBase):
    """Schema for retrieving an email notification."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    sender_id: int


class EmailSettingsBase(BaseModel):
    """Base schema for Email Settings model."""
    
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    use_tls: bool = True
    sender_email: EmailStr
    sender_name: str
    is_active: bool = True


class EmailSettingsCreate(EmailSettingsBase):
    """Schema for creating new email settings."""
    pass


class EmailSettingsUpdate(BaseModel):
    """Schema for updating email settings."""
    
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: Optional[bool] = None
    sender_email: Optional[EmailStr] = None
    sender_name: Optional[str] = None
    is_active: Optional[bool] = None


class EmailSettings(EmailSettingsBase):
    """Schema for retrieving email settings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class EmailSubscriptionBase(BaseModel):
    """Base schema for Email Subscription model."""
    
    general_notifications: bool = True
    announcement_notifications: bool = True
    homework_notifications: bool = True
    exam_notifications: bool = True
    event_notifications: bool = True
    report_notifications: bool = True
    attendance_notifications: bool = True
    fee_notifications: bool = True


class EmailSubscriptionCreate(EmailSubscriptionBase):
    """Schema for creating a new email subscription."""
    pass


class EmailSubscriptionUpdate(BaseModel):
    """Schema for updating an email subscription."""
    
    general_notifications: Optional[bool] = None
    announcement_notifications: Optional[bool] = None
    homework_notifications: Optional[bool] = None
    exam_notifications: Optional[bool] = None
    event_notifications: Optional[bool] = None
    report_notifications: Optional[bool] = None
    attendance_notifications: Optional[bool] = None
    fee_notifications: Optional[bool] = None


class EmailSubscription(EmailSubscriptionBase):
    """Schema for retrieving an email subscription."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class EmailSend(BaseModel):
    """Schema for sending an email."""
    
    to_emails: List[EmailStr]
    subject: str
    body: str
    cc_emails: Optional[List[EmailStr]] = None
    bcc_emails: Optional[List[EmailStr]] = None
    template_id: Optional[int] = None
    template_variables: Optional[dict] = None 