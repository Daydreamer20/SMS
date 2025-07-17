"""
School Management System - Main FastAPI Application
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import initialize_database, close_database_connections

# Create FastAPI app
app = FastAPI(
    title="School Management System API",
    description="API for School Management System",
    version="0.1.0",
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

# Configure CORS
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",  # React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    await initialize_database()


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