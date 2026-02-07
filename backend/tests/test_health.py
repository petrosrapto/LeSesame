"""
Le Sésame Backend - Health Endpoint Tests

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import pytest


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
