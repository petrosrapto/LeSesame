"""
Le Sésame Backend - Authentication Tests

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import pytest


@pytest.mark.asyncio
async def test_register_user(client, sample_user_data):
    """Test user registration returns token and user data."""
    response = await client.post("/auth/register", json=sample_user_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert data["user"]["username"] == sample_user_data["username"]


@pytest.mark.asyncio
async def test_register_duplicate_username(client, sample_user_data):
    """Test registration with duplicate username fails."""
    # First registration
    await client.post("/auth/register", json=sample_user_data)
    
    # Second registration with same username
    response = await client.post("/auth/register", json=sample_user_data)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_short_username(client):
    """Test registration with too short username fails."""
    response = await client.post("/auth/register", json={
        "username": "ab",  # Less than 3 characters
        "password": "testpass123"
    })
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(client, sample_user_data):
    """Test successful login returns token."""
    # Register first
    await client.post("/auth/register", json=sample_user_data)
    
    # Login
    response = await client.post("/auth/login", json={
        "username": sample_user_data["username"],
        "password": sample_user_data["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["user"]["username"] == sample_user_data["username"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, sample_user_data):
    """Test login with wrong password fails."""
    # Register first
    await client.post("/auth/register", json=sample_user_data)
    
    # Login with wrong password
    response = await client.post("/auth/login", json={
        "username": sample_user_data["username"],
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with non-existent user fails."""
    response = await client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "testpass123"
    })
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client, sample_user_data):
    """Test getting current user with valid token."""
    # Register and get token
    register_response = await client.post("/auth/register", json=sample_user_data)
    token = register_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == sample_user_data["username"]


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token fails."""
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
