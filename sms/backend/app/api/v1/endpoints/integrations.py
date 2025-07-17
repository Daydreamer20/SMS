"""
External integrations API endpoints.
"""

from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.api.v1.deps import get_current_active_user, get_current_admin, get_db
from app.core.database import get_db
from app.models.user import User
from app.models.integrations import ExternalApplication, APIKey, WebhookEndpoint, IntegrationLog
from app.schemas.integrations import (
    ExternalApplication as ExternalApplicationSchema,
    ExternalApplicationCreate,
    ExternalApplicationUpdate,
    APIKey as APIKeySchema,
    APIKeyCreate,
    APIKeyUpdate,
    WebhookEndpoint as WebhookEndpointSchema,
    WebhookEndpointCreate,
    WebhookEndpointUpdate,
    IntegrationLog as IntegrationLogSchema
)


router = APIRouter()


# API Key validation dependency
async def validate_api_key(
    api_key: str = Header(..., description="API Key for external applications"),
    db: AsyncSession = Depends(get_db)
) -> APIKey:
    """
    Validate API Key header and return the associated API Key.
    """
    result = await db.execute(
        select(APIKey).where(
            and_(
                APIKey.api_key == api_key,
                APIKey.is_active == True,
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > datetime.utcnow()
                )
            )
        )
    )
    api_key_obj = result.scalar_one_or_none()
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key_obj


# External Applications endpoints

@router.get("/applications", response_model=List[ExternalApplicationSchema])
async def read_external_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    integration_type: Optional[str] = None,
) -> Any:
    """
    Retrieve external applications.
    """
    query = select(ExternalApplication).offset(skip).limit(limit)
    
    filters = []
    if is_active is not None:
        filters.append(ExternalApplication.is_active == is_active)
    if integration_type:
        filters.append(ExternalApplication.integration_type == integration_type)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return applications


@router.post("/applications", response_model=ExternalApplicationSchema, status_code=status.HTTP_201_CREATED)
async def create_external_application(
    *,
    db: AsyncSession = Depends(get_db),
    application_in: ExternalApplicationCreate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Create a new external application.
    """
    application = ExternalApplication(**application_in.dict())
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@router.get("/applications/{application_id}", response_model=ExternalApplicationSchema)
async def read_external_application(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application to get"),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Get external application by ID.
    """
    result = await db.execute(select(ExternalApplication).where(ExternalApplication.id == application_id))
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="External application not found")
    
    return application


@router.put("/applications/{application_id}", response_model=ExternalApplicationSchema)
async def update_external_application(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application to update"),
    application_in: ExternalApplicationUpdate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Update an external application.
    """
    result = await db.execute(select(ExternalApplication).where(ExternalApplication.id == application_id))
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="External application not found")
    
    update_data = application_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    await db.commit()
    await db.refresh(application)
    return application


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_external_application(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application to delete"),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete an external application.
    """
    result = await db.execute(select(ExternalApplication).where(ExternalApplication.id == application_id))
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="External application not found")
    
    await db.delete(application)
    await db.commit()
    
    return None


# API Keys endpoints

@router.get("/applications/{application_id}/keys", response_model=List[APIKeySchema])
async def read_api_keys(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    current_user: User = Depends(get_current_admin),
    is_active: Optional[bool] = None,
) -> Any:
    """
    Retrieve API keys for a specific application.
    """
    # Verify application exists
    app_result = await db.execute(select(ExternalApplication).where(ExternalApplication.id == application_id))
    application = app_result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="External application not found")
    
    # Get API keys
    query = select(APIKey).where(APIKey.application_id == application_id)
    
    if is_active is not None:
        query = query.where(APIKey.is_active == is_active)
    
    result = await db.execute(query)
    api_keys = result.scalars().all()
    
    return api_keys


@router.post("/applications/{application_id}/keys", response_model=APIKeySchema, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    api_key_in: APIKeyCreate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Create a new API key for an application.
    """
    # Verify application exists
    app_result = await db.execute(select(ExternalApplication).where(ExternalApplication.id == application_id))
    application = app_result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="External application not found")
    
    # Create API key
    api_key = APIKey(
        **api_key_in.dict(),
        application_id=application_id,
        created_by_id=current_user.id
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return api_key


@router.put("/applications/{application_id}/keys/{key_id}", response_model=APIKeySchema)
async def update_api_key(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    key_id: int = Path(..., title="The ID of the API key to update"),
    api_key_in: APIKeyUpdate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Update an API key.
    """
    result = await db.execute(
        select(APIKey).where(
            and_(
                APIKey.id == key_id,
                APIKey.application_id == application_id
            )
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    update_data = api_key_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(api_key, field, value)
    
    await db.commit()
    await db.refresh(api_key)
    return api_key


@router.delete("/applications/{application_id}/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    key_id: int = Path(..., title="The ID of the API key to delete"),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete an API key.
    """
    result = await db.execute(
        select(APIKey).where(
            and_(
                APIKey.id == key_id,
                APIKey.application_id == application_id
            )
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    await db.delete(api_key)
    await db.commit()
    
    return None


# Webhook Endpoints endpoints

@router.get("/applications/{application_id}/webhooks", response_model=List[WebhookEndpointSchema])
async def read_webhook_endpoints(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    current_user: User = Depends(get_current_admin),
    is_active: Optional[bool] = None,
) -> Any:
    """
    Retrieve webhook endpoints for a specific application.
    """
    # Verify application exists
    app_result = await db.execute(select(ExternalApplication).where(ExternalApplication.id == application_id))
    application = app_result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="External application not found")
    
    # Get webhook endpoints
    query = select(WebhookEndpoint).where(WebhookEndpoint.application_id == application_id)
    
    if is_active is not None:
        query = query.where(WebhookEndpoint.is_active == is_active)
    
    result = await db.execute(query)
    webhooks = result.scalars().all()
    
    return webhooks


@router.post("/applications/{application_id}/webhooks", response_model=WebhookEndpointSchema, status_code=status.HTTP_201_CREATED)
async def create_webhook_endpoint(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    webhook_in: WebhookEndpointCreate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Create a new webhook endpoint for an application.
    """
    # Verify application exists
    app_result = await db.execute(select(ExternalApplication).where(ExternalApplication.id == application_id))
    application = app_result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="External application not found")
    
    # Create webhook endpoint
    webhook = WebhookEndpoint(
        **webhook_in.dict(),
        application_id=application_id
    )
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return webhook


@router.put("/applications/{application_id}/webhooks/{webhook_id}", response_model=WebhookEndpointSchema)
async def update_webhook_endpoint(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    webhook_id: int = Path(..., title="The ID of the webhook endpoint to update"),
    webhook_in: WebhookEndpointUpdate,
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Update a webhook endpoint.
    """
    result = await db.execute(
        select(WebhookEndpoint).where(
            and_(
                WebhookEndpoint.id == webhook_id,
                WebhookEndpoint.application_id == application_id
            )
        )
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    update_data = webhook_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(webhook, field, value)
    
    await db.commit()
    await db.refresh(webhook)
    return webhook


@router.delete("/applications/{application_id}/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook_endpoint(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    webhook_id: int = Path(..., title="The ID of the webhook endpoint to delete"),
    current_user: User = Depends(get_current_admin),
) -> Any:
    """
    Delete a webhook endpoint.
    """
    result = await db.execute(
        select(WebhookEndpoint).where(
            and_(
                WebhookEndpoint.id == webhook_id,
                WebhookEndpoint.application_id == application_id
            )
        )
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    await db.delete(webhook)
    await db.commit()
    
    return None


# Integration Logs endpoints

@router.get("/applications/{application_id}/logs", response_model=List[IntegrationLogSchema])
async def read_integration_logs(
    *,
    db: AsyncSession = Depends(get_db),
    application_id: int = Path(..., title="The ID of the application"),
    current_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    level: Optional[str] = None,
    success: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Any:
    """
    Retrieve integration logs for a specific application.
    """
    # Verify application exists
    app_result = await db.execute(select(ExternalApplication).where(ExternalApplication.id == application_id))
    application = app_result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="External application not found")
    
    # Get integration logs
    query = select(IntegrationLog).where(IntegrationLog.application_id == application_id)
    
    filters = []
    if level:
        filters.append(IntegrationLog.level == level)
    if success is not None:
        filters.append(IntegrationLog.success == success)
    if start_date:
        filters.append(IntegrationLog.created_at >= start_date)
    if end_date:
        filters.append(IntegrationLog.created_at <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(IntegrationLog.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs


# External API endpoints (accessible with API key)

@router.get("/data/students", tags=["external"])
async def get_students_data(
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(validate_api_key),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve student data for external applications.
    This is a sample endpoint that would provide data to integrated systems.
    """
    # Log the API request
    log = IntegrationLog(
        application_id=api_key.application_id,
        event="get_students_data",
        message="External API request to get students data",
        success=True
    )
    db.add(log)
    await db.commit()
    
    # Return sample response
    return {
        "message": "This is a placeholder for student data API that would be accessible via API key",
        "application": api_key.application.name,
        "status": "success"
    }


@router.get("/data/classes", tags=["external"])
async def get_classes_data(
    db: AsyncSession = Depends(get_db),
    api_key: APIKey = Depends(validate_api_key),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve class data for external applications.
    This is a sample endpoint that would provide data to integrated systems.
    """
    # Log the API request
    log = IntegrationLog(
        application_id=api_key.application_id,
        event="get_classes_data",
        message="External API request to get classes data",
        success=True
    )
    db.add(log)
    await db.commit()
    
    # Return sample response
    return {
        "message": "This is a placeholder for class data API that would be accessible via API key",
        "application": api_key.application.name,
        "status": "success"
    } 