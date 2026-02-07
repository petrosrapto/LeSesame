"""
Le Sésame Backend - Schema Validation Tests

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas import (
    UserCreate, UserResponse, TokenResponse, LoginRequest,
    ChatMessageRequest, PassphraseRequest, LevelInfo
)


class TestUserSchemas:
    """Test user-related schemas."""
    
    def test_user_create_valid(self):
        """Test valid user creation schema."""
        user = UserCreate(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        assert user.username == "testuser"
        assert user.password == "testpass123"
    
    def test_user_create_missing_password(self):
        """Test that missing password fails validation."""
        with pytest.raises(ValidationError):
            UserCreate(username="guest123", password=None, email=None)
    
    def test_user_create_short_password(self):
        """Test that short password fails validation."""
        with pytest.raises(ValidationError):
            UserCreate(username="testuser", password="12345")  # Less than 6 chars
    
    def test_user_create_short_username(self):
        """Test that short username fails validation."""
        with pytest.raises(ValidationError):
            UserCreate(username="ab", password="testpass")
    
    def test_user_create_long_username(self):
        """Test that too long username fails validation."""
        with pytest.raises(ValidationError):
            UserCreate(username="a" * 51, password="testpass")
    
    def test_login_request_valid(self):
        """Test valid login request schema."""
        login = LoginRequest(username="testuser", password="testpass")
        assert login.username == "testuser"
        assert login.password == "testpass"


class TestGameSchemas:
    """Test game-related schemas."""
    
    def test_chat_message_request_valid(self):
        """Test valid chat message request."""
        msg = ChatMessageRequest(message="Hello", level=1)
        assert msg.message == "Hello"
        assert msg.level == 1
    
    def test_chat_message_empty(self):
        """Test that empty message fails validation."""
        with pytest.raises(ValidationError):
            ChatMessageRequest(message="", level=1)
    
    def test_chat_message_invalid_level_low(self):
        """Test that level below 1 fails validation."""
        with pytest.raises(ValidationError):
            ChatMessageRequest(message="Hello", level=0)
    
    def test_chat_message_invalid_level_high(self):
        """Test that level above 5 fails validation."""
        with pytest.raises(ValidationError):
            ChatMessageRequest(message="Hello", level=6)
    
    def test_chat_message_too_long(self):
        """Test that too long message fails validation."""
        with pytest.raises(ValidationError):
            ChatMessageRequest(message="a" * 2001, level=1)
    
    def test_passphrase_request_valid(self):
        """Test valid passphrase request."""
        req = PassphraseRequest(passphrase="secret phrase", level=1)
        assert req.passphrase == "secret phrase"
        assert req.level == 1
    
    def test_passphrase_request_empty(self):
        """Test that empty passphrase fails validation."""
        with pytest.raises(ValidationError):
            PassphraseRequest(passphrase="", level=1)
    
    def test_level_info_valid(self):
        """Test valid level info schema."""
        level = LevelInfo(
            level=1,
            name="The Curious Assistant",
            description="First level",
            difficulty="easy",
            security_mechanism="Basic prompt",
            hints=["Hint 1", "Hint 2"]
        )
        assert level.level == 1
        assert level.completed is False
        assert level.attempts == 0
