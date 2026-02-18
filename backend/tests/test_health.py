"""
Le Sésame Backend - Health Endpoint Tests

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_health_check(client):
    """Test the health check endpoint returns healthy status."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "le-sesame-api"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_readiness_check(client):
    """Test the readiness check endpoint."""
    response = await client.get("/ready")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ready"
    assert data["service"] == "le-sesame-api"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test the root endpoint returns API information."""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "Le Sésame API"
    assert "version" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


@pytest.mark.asyncio
async def test_structured_output_metrics_no_data(client):
    """Test metrics endpoint when no calls have been made."""
    with patch("app.routers.health.get_structured_output_metrics", return_value={"total_calls": 0}):
        response = await client.get("/metrics/structured-output")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_data"
    assert "timestamp" in data
    assert "metrics" in data


@pytest.mark.asyncio
async def test_structured_output_metrics_healthy(client):
    """Test metrics endpoint with healthy json_schema success rate."""
    metrics = {"total_calls": 100, "json_schema_success_rate": 98, "overall_success_rate": 99}
    with patch("app.routers.health.get_structured_output_metrics", return_value=metrics):
        response = await client.get("/metrics/structured-output")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_structured_output_metrics_degraded(client):
    """Test metrics endpoint with degraded status."""
    metrics = {"total_calls": 100, "json_schema_success_rate": 50, "overall_success_rate": 92}
    with patch("app.routers.health.get_structured_output_metrics", return_value=metrics):
        response = await client.get("/metrics/structured-output")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"


@pytest.mark.asyncio
async def test_structured_output_metrics_critical(client):
    """Test metrics endpoint with critical status."""
    metrics = {"total_calls": 100, "json_schema_success_rate": 30, "overall_success_rate": 60}
    with patch("app.routers.health.get_structured_output_metrics", return_value=metrics):
        response = await client.get("/metrics/structured-output")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "critical"


@pytest.mark.asyncio
async def test_reset_structured_output_metrics(client):
    """Test reset metrics endpoint."""
    with patch("app.routers.health.reset_structured_output_metrics") as mock_reset:
        response = await client.post("/metrics/structured-output/reset")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reset"
    assert "timestamp" in data
    mock_reset.assert_called_once()
