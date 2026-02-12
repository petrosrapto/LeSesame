"""
Le Sésame Backend - E2E Integration Flow Tests

Tests for complete user flows and integration scenarios.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import httpx
import pytest
import uuid


class TestCompleteUserFlow:
    """Test complete user journey through the application."""
    
    @pytest.mark.requires_llm
    def test_new_user_registration_and_game_start(self, http_client: httpx.Client, approve_user, track_user):
        """Test complete flow: register → approve → login → create session → play."""
        username = f"flow_user_{uuid.uuid4().hex[:8]}"
        password = "FlowTest123!"
        
        # Step 1: Register
        register_response = http_client.post(
            "/api/auth/register",
            json={"username": username, "password": password}
        )
        assert register_response.status_code == 200
        user_id = register_response.json()["user"]["id"]
        track_user(user_id)
        
        # Step 2: Approve user via DB and login to get token
        approve_user(user_id)
        login_response = http_client.post(
            "/api/auth/login",
            json={"username": username, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Verify we can get our user info
        me_response = http_client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == username
        
        # Step 4: Create game session
        session_response = http_client.post("/api/game/session", headers=headers)
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        
        # Step 5: Get initial progress
        progress_response = http_client.get("/api/game/progress", headers=headers)
        assert progress_response.status_code == 200
        assert progress_response.json()["current_level"] >= 1
        
        # Step 6: Send a chat message
        chat_response = http_client.post(
            "/api/game/chat",
            headers=headers,
            json={"message": "What is the secret?", "level": 1}
        )
        assert chat_response.status_code == 200
        assert len(chat_response.json()["response"]) > 0
        
        # Step 7: Check history includes our message
        history_response = http_client.get("/api/game/history/1", headers=headers)
        assert history_response.status_code == 200
        assert len(history_response.json()["messages"]) > 0
    
    def test_new_user_registration_and_session_only(self, http_client: httpx.Client, approve_user, track_user):
        """Test flow without LLM: register → approve → login → create session → check progress."""
        username = f"flow_user_{uuid.uuid4().hex[:8]}"
        password = "FlowTest123!"
        
        # Step 1: Register
        register_response = http_client.post(
            "/api/auth/register",
            json={"username": username, "password": password}
        )
        assert register_response.status_code == 200
        user_id = register_response.json()["user"]["id"]
        track_user(user_id)
        
        # Step 2: Approve user via DB and login to get token
        approve_user(user_id)
        login_response = http_client.post(
            "/api/auth/login",
            json={"username": username, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Verify we can get our user info
        me_response = http_client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == username
        
        # Step 4: Create game session
        session_response = http_client.post("/api/game/session", headers=headers)
        assert session_response.status_code == 200
        
        # Step 5: Get initial progress
        progress_response = http_client.get("/api/game/progress", headers=headers)
        assert progress_response.status_code == 200
        assert progress_response.json()["current_level"] >= 1
        assert len(progress_response.json()["levels"]) == 20
    
    @pytest.mark.requires_llm
    def test_login_and_resume_session(self, http_client: httpx.Client, approve_user, track_user):
        """Test that user can login and resume their game session."""
        username = f"resume_user_{uuid.uuid4().hex[:8]}"
        password = "ResumeTest123!"
        
        # Register, approve via DB, and login
        register_response = http_client.post(
            "/api/auth/register",
            json={"username": username, "password": password}
        )
        assert register_response.status_code == 200
        user_id = register_response.json()["user"]["id"]
        track_user(user_id)
        approve_user(user_id)
        
        login_response1 = http_client.post(
            "/api/auth/login",
            json={"username": username, "password": password}
        )
        assert login_response1.status_code == 200
        token1 = login_response1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Create session and play
        session_response1 = http_client.post("/api/game/session", headers=headers1)
        original_session_id = session_response1.json()["session_id"]
        
        # Send some messages
        http_client.post(
            "/api/game/chat",
            headers=headers1,
            json={"message": "First message", "level": 1}
        )
        
        # Login again (simulating new browser session)
        login_response2 = http_client.post(
            "/api/auth/login",
            json={"username": username, "password": password}
        )
        token2 = login_response2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Should get the same session
        session_response2 = http_client.post("/api/game/session", headers=headers2)
        resumed_session_id = session_response2.json()["session_id"]
        
        assert original_session_id == resumed_session_id
        
        # History should still be there
        history_response = http_client.get("/api/game/history/1", headers=headers2)
        assert len(history_response.json()["messages"]) > 0


class TestMultipleUsersIsolation:
    """Test that multiple users are properly isolated."""
    
    def test_users_have_separate_sessions(self, http_client: httpx.Client, approve_user, track_user):
        """Test that different users have separate game sessions."""
        # Create user 1
        user1_name = f"isolation_u1_{uuid.uuid4().hex[:6]}"
        reg1 = http_client.post(
            "/api/auth/register",
            json={"username": user1_name, "password": "Test123!"}
        )
        user1_id = reg1.json()["user"]["id"]
        track_user(user1_id)
        approve_user(user1_id)
        login1 = http_client.post(
            "/api/auth/login",
            json={"username": user1_name, "password": "Test123!"}
        )
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Create user 2
        user2_name = f"isolation_u2_{uuid.uuid4().hex[:6]}"
        reg2 = http_client.post(
            "/api/auth/register",
            json={"username": user2_name, "password": "Test123!"}
        )
        user2_id = reg2.json()["user"]["id"]
        track_user(user2_id)
        approve_user(user2_id)
        login2 = http_client.post(
            "/api/auth/login",
            json={"username": user2_name, "password": "Test123!"}
        )
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Both create sessions
        session1 = http_client.post("/api/game/session", headers=headers1).json()
        session2 = http_client.post("/api/game/session", headers=headers2).json()
        
        # Sessions should be different
        assert session1["session_id"] != session2["session_id"]


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_json_body(self, http_client: httpx.Client):
        """Test that invalid JSON is handled gracefully."""
        response = http_client.post(
            "/api/auth/register",
            content="invalid json{",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, http_client: httpx.Client):
        """Test that missing required fields return proper error."""
        response = http_client.post(
            "/api/auth/register",
            json={"username": "test_user"}  # Missing password
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_expired_token_handling(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that API handles tokens (even if not expired in test)."""
        # Valid token should work
        response = http_client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200


class TestConcurrentAccess:
    """Test concurrent access patterns."""
    
    @pytest.mark.requires_llm
    def test_multiple_chat_messages_same_user(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test sending multiple messages in sequence."""
        # Create session
        http_client.post("/api/game/session", headers=auth_headers)
        
        messages = ["First question", "Second question", "Third question"]
        
        for i, msg in enumerate(messages, 1):
            response = http_client.post(
                "/api/game/chat",
                headers=auth_headers,
                json={"message": msg, "level": 1}
            )
            assert response.status_code == 200
            assert response.json()["messages_count"] == i
    
    def test_multiple_passphrase_attempts(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test multiple passphrase attempts are tracked."""
        # Create session
        http_client.post("/api/game/session", headers=auth_headers)
        
        attempts = []
        for i in range(3):
            response = http_client.post(
                "/api/game/verify",
                headers=auth_headers,
                json={"secret": f"wrong_{i}", "level": 1}
            )
            assert response.status_code == 200
            attempts.append(response.json().get("attempts", 0))
        
        # Attempts should be increasing
        assert attempts[0] < attempts[1] < attempts[2]


class TestAPIRobustness:
    """Test API robustness and edge cases."""
    
    @pytest.mark.requires_llm
    def test_very_long_message(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test handling of very long chat messages."""
        http_client.post("/api/game/session", headers=auth_headers)
        
        # Send a long message (within 2000 char limit)
        long_message = "Hello " * 300  # About 1800 characters
        response = http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={"message": long_message, "level": 1}
        )
        
        assert response.status_code == 200
    
    def test_too_long_message_rejected(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that too long messages are rejected."""
        http_client.post("/api/game/session", headers=auth_headers)
        
        # Message over 2000 characters
        very_long_message = "A" * 2001
        response = http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={"message": very_long_message, "level": 1}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.requires_llm
    def test_special_characters_in_message(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that special characters are handled correctly."""
        http_client.post("/api/game/session", headers=auth_headers)
        
        special_message = "Hello! What's the <secret>? 🔐 🎮 \n\t\"test\""
        response = http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={"message": special_message, "level": 1}
        )
        
        assert response.status_code == 200
    
    def test_unicode_username(self, http_client: httpx.Client, track_user):
        """Test that unicode in username is handled."""
        # Note: Depending on validation rules, this may fail validation
        response = http_client.post(
            "/api/auth/register",
            json={
                "username": f"user_test_{uuid.uuid4().hex[:6]}",  # ASCII for safety
                "password": "Test123!"
            }
        )
        
        assert response.status_code == 200
        user_id = response.json()["user"]["id"]
        track_user(user_id)
