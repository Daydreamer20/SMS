"""
Tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Role
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, db: AsyncSession) -> None:
    """
    Test creating a user.
    """
    # First, create a role
    admin_role = Role(name="admin", description="Administrator")
    db.add(admin_role)
    await db.commit()
    await db.refresh(admin_role)

    # Create user data
    data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "username": "testuser",
        "role": "admin"
    }

    response = await client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "test@example.com"
    assert user_data["full_name"] == "Test User"
    assert user_data["username"] == "testuser"
    assert "password" not in user_data


@pytest.mark.asyncio
async def test_login(client: AsyncClient, db: AsyncSession) -> None:
    """
    Test user login.
    """
    # First, create a role
    admin_role = Role(name="admin", description="Administrator")
    db.add(admin_role)
    await db.commit()
    await db.refresh(admin_role)

    # Create a user for testing login
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        role=admin_role.name,
        password_hash=hashed_password,
        is_active=True
    )
    db.add(user)
    await db.commit()

    # Login data
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, db: AsyncSession) -> None:
    """
    Test login with invalid credentials.
    """
    # First, create a role
    admin_role = Role(name="admin", description="Administrator")
    db.add(admin_role)
    await db.commit()
    await db.refresh(admin_role)

    # Create a user
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        role=admin_role.name,
        password_hash=hashed_password,
        is_active=True
    )
    db.add(user)
    await db.commit()

    # Invalid login data
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }

    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, db: AsyncSession) -> None:
    """
    Test getting current user with token.
    """
    # First, create a role
    admin_role = Role(name="admin", description="Administrator")
    db.add(admin_role)
    await db.commit()
    await db.refresh(admin_role)

    # Create a user
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        role=admin_role.name,
        password_hash=hashed_password,
        is_active=True
    )
    db.add(user)
    await db.commit()

    # Login to get token
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    token_data = response.json()
    access_token = token_data["access_token"]

    # Get current user with token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "test@example.com"
    assert user_data["username"] == "testuser" 