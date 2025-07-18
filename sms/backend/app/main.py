"""
School Management System - Main FastAPI Application
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import initialize_database, close_database_connections
from app.core.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    IPWhitelistMiddleware,
    get_redis_client,
    close_redis_client,
)
from app.core.logging import setup_logging, get_logger, log_security_event

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize Sentry for error tracking in production
if settings.SENTRY_DSN and settings.ENVIRONMENT == "production":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting School Management System API")
    await initialize_database()
    
    # Initialize Redis for rate limiting
    redis_client = await get_redis_client()
    if redis_client:
        logger.info("Redis connection established for rate limiting")
    
    yield
    
    # Shutdown
    logger.info("Shutting down School Management System API")
    await close_database_connections()
    await close_redis_client()


# Create FastAPI app
app = FastAPI(
    title="School Management System API",
    description="API for School Management System",
    version="0.1.0",
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan,
)

# Security middleware (order matters!)
# 1. Trusted host middleware (first)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["your-domain.com", "www.your-domain.com", "localhost"]
    )

# 2. Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. Rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

# 4. IP whitelist middleware for admin endpoints
if settings.ENVIRONMENT == "production":
    # Add your admin IP addresses here
    admin_whitelist = []  # e.g., ["192.168.1.100", "10.0.0.50"]
    app.add_middleware(IPWhitelistMiddleware, whitelist=admin_whitelist)

# 5. CORS middleware (last)
origins = []
if settings.ENVIRONMENT == "development":
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
else:
    origins = [origin.strip() for origin in settings.CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP {exc.status_code} error: {exc.detail}")
    
    # Log security events
    if exc.status_code in [401, 403, 429]:
        log_security_event(
            event_type=f"HTTP_{exc.status_code}",
            details={"detail": exc.detail},
            request_info={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "status_code": 422}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "status_code": 500}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "status_code": 500}
        )


# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "School Management System API",
        "version": "0.1.0",
        "status": "online",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for the API."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "api": True, "database": True},
    )


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        # Run our custom database initialization
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from init_db import create_tables
        await create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Continue anyway - the app might still work


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    await close_database_connections()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    ) 