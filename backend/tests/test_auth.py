"""
Le Sésame Backend - Authentication Tests

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import pytest
from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_register_user(client, sample_user_data):
    """Test user registration returns message and user data (pending email verification)."""
    response = await client.post("/api/auth/register", json=sample_user_data)

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert data["user"]["username"] == sample_user_data["username"]
    assert data["user"]["is_approved"] is True
    assert data["user"]["email_verified"] is False


@pytest.mark.asyncio
async def test_register_duplicate_username(client, sample_user_data):
    """Test registration with duplicate username fails."""
    await client.post("/api/auth/register", json=sample_user_data)
    dup = {**sample_user_data, "email": "other@example.com"}
    response = await client.post("/api/auth/register", json=dup)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_short_username(client):
    """Test registration with too short username fails."""
    response = await client.post("/api/auth/register", json={
        "username": "ab",
        "password": "testpass123",
        "email": "ab@example.com",
        "captcha_token": "test",
    })

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_unverified_email(client, sample_user_data):
    """Test that users with unverified email cannot login."""
    await client.post("/api/auth/register", json=sample_user_data)

    response = await client.post("/api/auth/login", json={
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
        "captcha_token": "test",
    })

    assert response.status_code == 403
    assert "verify your email" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client, sample_user_data):
    """Test successful login returns token (after approval)."""
    token = await register_and_login(client, sample_user_data)
    assert token is not None and len(token) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client, sample_user_data):
    """Test login with wrong password fails."""
    await register_and_login(client, sample_user_data)

    response = await client.post("/api/auth/login", json={
        "username": sample_user_data["username"],
        "password": "wrongpassword",
        "captcha_token": "test",
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with non-existent user fails."""
    response = await client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "testpass123",
        "captcha_token": "test",
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client, sample_user_data):
    """Test getting current user with valid token."""
    token = await register_and_login(client, sample_user_data)

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == sample_user_data["username"]


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token fails."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401
