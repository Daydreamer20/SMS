"""
Monitoring and health check endpoints.
"""

import asyncio
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_redis_client

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "0.1.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with all dependencies."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        start_time = time.time()
        result = await db.execute(text("SELECT 1"))
        db_response_time = time.time() - start_time
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time": round(db_response_time * 1000, 2),  # ms
            "details": "Connection successful"
        }
    except Exception as e:
        overall_healthy = False
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Redis health check
    try:
        redis_client = await get_redis_client()
        if redis_client:
            start_time = time.time()
            await redis_client.ping()
            redis_response_time = time.time() - start_time
            
            health_status["checks"]["redis"] = {
                "status": "healthy",
                "response_time": round(redis_response_time * 1000, 2),  # ms
                "details": "Connection successful"
            }
        else:
            health_status["checks"]["redis"] = {
                "status": "disabled",
                "details": "Redis not configured"
            }
    except Exception as e:
        overall_healthy = False
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Set overall status
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    
    # Return appropriate HTTP status
    if not overall_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status


@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Get application metrics."""
    metrics = {
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT,
        "database": {},
        "redis": {},
        "system": {}
    }
    
    # Database metrics
    try:
        # Get database size
        result = await db.execute(text("""
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as db_size,
                (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') as table_count
        """))
        db_info = result.fetchone()
        
        # Get connection count
        conn_result = await db.execute(text("""
            SELECT count(*) as active_connections 
            FROM pg_stat_activity 
            WHERE state = 'active'
        """))
        conn_info = conn_result.fetchone()
        
        metrics["database"] = {
            "size": db_info[0] if db_info else "unknown",
            "table_count": db_info[1] if db_info else 0,
            "active_connections": conn_info[0] if conn_info else 0
        }
    except Exception as e:
        metrics["database"]["error"] = str(e)
    
    # Redis metrics
    try:
        redis_client = await get_redis_client()
        if redis_client:
            info = await redis_client.info()
            metrics["redis"] = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        else:
            metrics["redis"] = {"status": "disabled"}
    except Exception as e:
        metrics["redis"]["error"] = str(e)
    
    return metrics


@router.get("/readiness")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe endpoint."""
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        
        # Check Redis if enabled
        if settings.RATE_LIMIT_ENABLED:
            redis_client = await get_redis_client()
            if redis_client:
                await redis_client.ping()
        
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not ready", "error": str(e)}
        )


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive", "timestamp": time.time()}