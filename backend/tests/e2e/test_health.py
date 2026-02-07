"""
Le Sésame Backend - E2E Health Endpoint Tests

Tests for health and readiness endpoints.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import httpx
import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_endpoint_returns_healthy(self, http_client: httpx.Client):
        """Test that /health returns healthy status."""
        response = http_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "le-sesame-api"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    def test_ready_endpoint_returns_ready(self, http_client: httpx.Client):
        """Test that /ready returns ready status."""
        response = http_client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "le-sesame-api"
        assert "timestamp" in data


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_schema_available(self, http_client: httpx.Client):
        """Test that OpenAPI schema is available."""
        response = http_client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Le Sésame API"
    
    def test_swagger_docs_available(self, http_client: httpx.Client):
        """Test that Swagger UI docs are available."""
        response = http_client.get("/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
