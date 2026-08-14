"""Unit and integration tests for health endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_top_level_health_endpoint():
    """Test GET /health returns expected status and metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DecisionOS API"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "development"


def test_versioned_health_endpoint():
    """Test GET /api/v1/health returns expected status and metadata."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DecisionOS API"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "development"


def test_root_endpoint():
    """Test GET / returns root system info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "DecisionOS API"
    assert data["health_check"] == "/health"
    assert data["api_v1"] == "/api/v1"
