"""
API endpoint tests for chat persistence system.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from src.api import app
from src.database import db_manager

client = TestClient(app)

@pytest.fixture
async def setup_database():
    """Setup test database"""
    await db_manager.initialize()
    yield
    # Cleanup would go here

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

def test_get_chat_history():
    """Test chat history endpoint"""
    response = client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

def test_get_usage_stats():
    """Test usage statistics endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_interactions" in data
    assert "unique_sessions" in data

def test_pagination():
    """Test pagination parameters"""
    response = client.get("/history?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5
    assert data["offset"] == 0

if __name__ == "__main__":
    pytest.main([__file__])
