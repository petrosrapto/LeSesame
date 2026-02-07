"""
Le Sésame Backend - E2E Authentication Tests

Tests for user registration, login, and authentication flows.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import httpx
import pytest


class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_new_user_success(
        self, 
        http_client: httpx.Client, 
        unique_username: str, 
        test_password: str
    ):
        """Test successful user registration."""
        response = http_client.post(
            "/api/auth/register",
            json={
                "username": unique_username,
                "password": test_password,
                "email": f"{unique_username}@example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify token response structure
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0
        
        # Verify user response structure
        assert "user" in data
        assert data["user"]["username"] == unique_username
        assert "id" in data["user"]
        assert "created_at" in data["user"]
    
    def test_register_duplicate_username_fails(
        self, 
        http_client: httpx.Client, 
        registered_user: dict, 
        test_password: str
    ):
        """Test that registering with an existing username fails."""
        response = http_client.post(
            "/api/auth/register",
            json={
                "username": registered_user["username"],
                "password": test_password
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_register_short_username_fails(
        self, 
        http_client: httpx.Client, 
        test_password: str
    ):
        """Test that registration fails with too short username."""
        response = http_client.post(
            "/api/auth/register",
            json={
                "username": "ab",  # Too short (min 3)
                "password": test_password
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_short_password_fails(
        self, 
        http_client: httpx.Client, 
        unique_username: str
    ):
        """Test that registration fails with too short password."""
        response = http_client.post(
            "/api/auth/register",
            json={
                "username": unique_username,
                "password": "12345"  # Too short (min 6)
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(
        self, 
        http_client: httpx.Client, 
        registered_user: dict
    ):
        """Test successful login with valid credentials."""
        response = http_client.post(
            "/api/auth/login",
            json={
                "username": registered_user["username"],
                "password": registered_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify token response
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        
        # Verify user info
        assert data["user"]["username"] == registered_user["username"]
    
    def test_login_wrong_password_fails(
        self, 
        http_client: httpx.Client, 
        registered_user: dict
    ):
        """Test login fails with wrong password."""
        response = http_client.post(
            "/api/auth/login",
            json={
                "username": registered_user["username"],
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid credentials" in data["detail"].lower()
    
    def test_login_nonexistent_user_fails(self, http_client: httpx.Client):
        """Test login fails for non-existent user."""
        response = http_client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent_user_xyz",
                "password": "any_password"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid credentials" in data["detail"].lower()


class TestCurrentUser:
    """Test current user endpoint."""
    
    def test_get_me_authenticated(
        self, 
        http_client: httpx.Client, 
        registered_user: dict, 
        auth_headers: dict
    ):
        """Test getting current user info when authenticated."""
        response = http_client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == registered_user["username"]
        assert data["id"] == registered_user["user_id"]
    
    def test_get_me_unauthenticated(self, http_client: httpx.Client):
        """Test getting current user info without authentication fails."""
        response = http_client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    def test_get_me_invalid_token(self, http_client: httpx.Client):
        """Test getting current user info with invalid token fails."""
        response = http_client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
