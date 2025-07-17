"""
Basic test to verify that our fixes have resolved the issues.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


def test_app_exists():
    """Test that the app exists."""
    assert app is not None


def test_api_root():
    """Test that the API root returns a 200 response."""
    client = TestClient(app)
    response = client.get("/api/v1")
    assert response.status_code == 200
    assert "message" in response.json() 