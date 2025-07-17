"""
Email notification API endpoints.
"""

from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.api.v1.deps import get_current_active_user, get_current_admin, get_db
from app.core.database import get_db
from app.models.user import User
from app.models.email import EmailTemplate, EmailNotification, EmailSettings, EmailSubscription, EmailStatus
from app.schemas.email import (
    EmailTemplate as EmailTemplateSchema,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailNotification as EmailNotificationSchema,
    EmailNotificationCreate,
    EmailNotificationUpdate,
    EmailSettings as EmailSettingsSchema,
    EmailSettingsCreate,
    EmailSettingsUpdate,
    EmailSubscription as EmailSubscriptionSchema,
    EmailSubscriptionCreate,
    EmailSubscriptionUpdate,
    EmailSend
)

# Email sending utility function - placeholder
async def send_email_async(
    db: AsyncSession,
    notification_id: int,
) -> None:
    """
    Send email asynchronously.
    This is a placeholder function that should be implemented with actual email sending logic.
    It updates the status of the email notification after sending.
    """
    # Get the notification
    result = await db.execute(select(EmailNotification).where(EmailNotification.id == notification_id))
    notification = result.scalar_one_or_none()
    
    if not notification:
        return
    
    # Get email settings
    settings_result = await db.execute(select(EmailSettings).where(EmailSettings.is_active == True).limit(1))
    settings = settings_result.scalar_one_or_none()
    
    if not settings:
        notification.status = EmailStatus.FAILED.value
        notification.error_message = "Email settings not configured"
        await db.commit()
        return
    
    # TODO: Implement actual email sending logic using SMTP or an email service provider
    
    try:
        # Simulate email sending success (should be replaced with actual email sending)
        notification.status = EmailStatus.SENT.value
        notification.sent_at = datetime.utcnow()
    except Exception as e:
        notification.status = EmailStatus.FAILED.value
        notification.error_message = str(e)
    
    await db.commit()


router = APIRouter()


# Email Templates endpoints

@router.get("/templates", response_model=List[EmailTemplateSchema])
async def read_email_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    email_type: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Any:
    """
    Retrieve email templates.
    """
    query = select(EmailTemplate).offset(skip).limit(limit)
    
    # Apply filters
    filters = []
    if email_type:
        filters.append(EmailTemplate.email_type == email_type)
    if is_active is not None:
        filters.append(EmailTemplate.is_active == is_active)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return templates


@router.post("/templates", response_model=EmailTemplateSchema, status_code=status.HTTP_201_CREATED)
async def create_email_template(
    *,
    db: AsyncSession = Depends(get_db),
    template_in: EmailTemplateCreate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Create a new email template.
    """
    template = EmailTemplate(**template_in.dict())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get("/templates/{template_id}", response_model=EmailTemplateSchema)
async def read_email_template(
    *,
    db: AsyncSession = Depends(get_db),
    template_id: int = Path(..., title="The ID of the template to get"),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Get email template by ID.
    """
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")
    
    return template


@router.put("/templates/{template_id}", response_model=EmailTemplateSchema)
async def update_email_template(
    *,
    db: AsyncSession = Depends(get_db),
    template_id: int = Path(..., title="The ID of the template to update"),
    template_in: EmailTemplateUpdate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Update an email template.
    """
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")
    
    update_data = template_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_template(
    *,
    db: AsyncSession = Depends(get_db),
    template_id: int = Path(..., title="The ID of the template to delete"),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete an email template.
    """
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")
    
    await db.delete(template)
    await db.commit()
    
    return None


# Email Notifications endpoints

@router.get("/notifications", response_model=List[EmailNotificationSchema])
async def read_email_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Any:
    """
    Retrieve email notifications.
    """
    query = select(EmailNotification).offset(skip).limit(limit)
    
    # Apply filters
    filters = []
    if status:
        filters.append(EmailNotification.status == status)
    if start_date:
        filters.append(EmailNotification.created_at >= start_date)
    if end_date:
        filters.append(EmailNotification.created_at <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return notifications


@router.post("/send", response_model=EmailNotificationSchema, status_code=status.HTTP_201_CREATED)
async def send_email(
    *,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks,
    email_in: EmailSend,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Send an email.
    """
    # Check if email settings are configured
    settings_result = await db.execute(select(EmailSettings).where(EmailSettings.is_active == True).limit(1))
    settings = settings_result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(status_code=400, detail="Email settings not configured")
    
    # Create a notification for the first recipient
    notification = EmailNotification(
        subject=email_in.subject,
        body=email_in.body,
        recipient_email=email_in.to_emails[0],
        template_id=email_in.template_id,
        sender_id=current_user.id
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    # Queue the email sending task
    background_tasks.add_task(send_email_async, db, notification.id)
    
    # For multiple recipients, create additional notifications
    if len(email_in.to_emails) > 1:
        for recipient in email_in.to_emails[1:]:
            additional_notification = EmailNotification(
                subject=email_in.subject,
                body=email_in.body,
                recipient_email=recipient,
                template_id=email_in.template_id,
                sender_id=current_user.id
            )
            db.add(additional_notification)
            await db.commit()
            await db.refresh(additional_notification)
            
            # Queue additional email sending task
            background_tasks.add_task(send_email_async, db, additional_notification.id)
    
    return notification


@router.get("/notifications/{notification_id}", response_model=EmailNotificationSchema)
async def read_email_notification(
    *,
    db: AsyncSession = Depends(get_db),
    notification_id: int = Path(..., title="The ID of the notification to get"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get email notification by ID.
    """
    result = await db.execute(select(EmailNotification).where(EmailNotification.id == notification_id))
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Email notification not found")
    
    # Check if user has permission to view this notification
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if not (is_admin or notification.sender_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions to access this notification")
    
    return notification


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_notification(
    *,
    db: AsyncSession = Depends(get_db),
    notification_id: int = Path(..., title="The ID of the notification to delete"),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete an email notification.
    """
    result = await db.execute(select(EmailNotification).where(EmailNotification.id == notification_id))
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Email notification not found")
    
    await db.delete(notification)
    await db.commit()
    
    return None


# Email Settings endpoints

@router.get("/settings", response_model=EmailSettingsSchema)
async def read_email_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Retrieve email settings.
    """
    result = await db.execute(select(EmailSettings).limit(1))
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Email settings not found")
    
    return settings


@router.post("/settings", response_model=EmailSettingsSchema, status_code=status.HTTP_201_CREATED)
async def create_email_settings(
    *,
    db: AsyncSession = Depends(get_db),
    settings_in: EmailSettingsCreate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Create or update email settings.
    """
    # Check if settings already exist
    result = await db.execute(select(EmailSettings).limit(1))
    existing_settings = result.scalar_one_or_none()
    
    if existing_settings:
        # Update existing settings
        update_data = settings_in.dict()
        for field, value in update_data.items():
            setattr(existing_settings, field, value)
        
        await db.commit()
        await db.refresh(existing_settings)
        return existing_settings
    else:
        # Create new settings
        settings = EmailSettings(**settings_in.dict())
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
        return settings


@router.put("/settings/{settings_id}", response_model=EmailSettingsSchema)
async def update_email_settings(
    *,
    db: AsyncSession = Depends(get_db),
    settings_id: int = Path(..., title="The ID of the settings to update"),
    settings_in: EmailSettingsUpdate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Update email settings.
    """
    result = await db.execute(select(EmailSettings).where(EmailSettings.id == settings_id))
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Email settings not found")
    
    update_data = settings_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    return settings


# Email Subscription endpoints

@router.get("/subscriptions/me", response_model=EmailSubscriptionSchema)
async def read_my_email_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve the current user's email subscription settings.
    """
    result = await db.execute(
        select(EmailSubscription).where(EmailSubscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Create default subscription settings if not exists
        subscription = EmailSubscription(user_id=current_user.id)
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
    
    return subscription


@router.put("/subscriptions/me", response_model=EmailSubscriptionSchema)
async def update_my_email_subscriptions(
    *,
    db: AsyncSession = Depends(get_db),
    subscription_in: EmailSubscriptionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update the current user's email subscription settings.
    """
    result = await db.execute(
        select(EmailSubscription).where(EmailSubscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Create new subscription with provided settings
        subscription_data = subscription_in.dict(exclude_unset=True)
        subscription = EmailSubscription(user_id=current_user.id, **subscription_data)
        db.add(subscription)
    else:
        # Update existing subscription
        update_data = subscription_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subscription, field, value)
    
    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.get("/subscriptions", response_model=List[EmailSubscriptionSchema])
async def read_all_email_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all users' email subscription settings.
    """
    query = select(EmailSubscription).offset(skip).limit(limit)
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return subscriptions 