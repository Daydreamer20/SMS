"""
Pytest configuration for SMS backend tests.
"""

import asyncio
import os
from typing import AsyncGenerator, Dict, Generator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Test database URL
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    f"sqlite+aiosqlite:///./test_db.db"
)


# Create async engine for tests
test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_async_engine,
    class_=AsyncSession,
)


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database for each test.
    """
    # Create the database and tables
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Run the tests
    async with TestingSessionLocal() as session:
        yield session

    # Drop the database after the tests
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Override the get_db dependency
@pytest.fixture
def override_get_db(db: AsyncSession) -> None:
    """
    Override the get_db dependency for tests.
    """

    async def _get_test_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    return None


@pytest.fixture
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async client for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an event loop for tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 