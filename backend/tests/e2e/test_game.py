"""
Le Sésame Backend - E2E Game Tests

Tests for game session, chat, passphrase verification, and progress endpoints.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import httpx
import pytest


class TestGameSession:
    """Test game session management."""
    
    def test_create_session_authenticated(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test creating a game session when authenticated."""
        response = http_client.post("/api/game/session", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert data["current_level"] >= 1
        assert "started_at" in data
    
    def test_create_session_unauthenticated_fails(self, http_client: httpx.Client):
        """Test creating a session without authentication fails."""
        response = http_client.post("/api/game/session")
        
        assert response.status_code == 401
    
    def test_session_persistence(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that session persists across requests."""
        # Create first session
        response1 = http_client.post("/api/game/session", headers=auth_headers)
        assert response1.status_code == 200
        session1 = response1.json()
        
        # Request session again
        response2 = http_client.post("/api/game/session", headers=auth_headers)
        assert response2.status_code == 200
        session2 = response2.json()
        
        # Should return the same session
        assert session1["session_id"] == session2["session_id"]


class TestChatEndpoint:
    """Test chat messaging endpoint."""
    
    @pytest.mark.requires_llm
    def test_send_chat_message_success(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test sending a chat message to the AI guardian."""
        # First create a session
        http_client.post("/api/game/session", headers=auth_headers)
        
        response = http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={
                "message": "Hello, what is the secret?",
                "level": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "response" in data
        assert data["level"] == 1
        assert "attempts" in data
        assert "messages_count" in data
        assert len(data["response"]) > 0  # AI should respond
    
    @pytest.mark.requires_llm
    def test_send_chat_invalid_level_fails(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that sending chat to invalid level fails."""
        response = http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={
                "message": "Hello",
                "level": 10  # Invalid level
            }
        )
        
        # Pydantic validation returns 422 for out-of-range values
        assert response.status_code == 422
    
    def test_send_chat_level_0_fails(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that level 0 is invalid."""
        response = http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={
                "message": "Hello",
                "level": 0
            }
        )
        
        assert response.status_code == 422  # Validation error (ge=1)
    
    def test_send_chat_unauthenticated_fails(self, http_client: httpx.Client):
        """Test sending chat without authentication fails."""
        response = http_client.post(
            "/api/game/chat",
            json={
                "message": "Hello",
                "level": 1
            }
        )
        
        assert response.status_code == 401
    
    def test_send_empty_message_fails(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test sending empty message fails validation."""
        response = http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={
                "message": "",
                "level": 1
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestPassphraseVerification:
    """Test passphrase verification endpoint."""
    
    def test_verify_wrong_passphrase(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that wrong secret returns failure."""
        # Create session first
        http_client.post("/api/game/session", headers=auth_headers)
        
        response = http_client.post(
            "/api/game/verify",
            headers=auth_headers,
            json={
                "secret": "wrong_secret_123",
                "level": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert data["level"] == 1
        assert "incorrect" in data["message"].lower() or "❌" in data["message"]
        assert data["secret"] is None
    
    def test_verify_invalid_level_fails(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that verification fails for invalid level."""
        response = http_client.post(
            "/api/game/verify",
            headers=auth_headers,
            json={
                "secret": "test",
                "level": 10
            }
        )
        
        # Pydantic validation returns 422 for out-of-range values
        assert response.status_code == 422
    
    def test_verify_unauthenticated_fails(self, http_client: httpx.Client):
        """Test that verification without auth fails."""
        response = http_client.post(
            "/api/game/verify",
            json={
                "secret": "test",
                "level": 1
            }
        )
        
        assert response.status_code == 401
    
    def test_verify_attempts_increment(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that attempts counter increments on each try."""
        # Create session
        http_client.post("/api/game/session", headers=auth_headers)
        
        # First attempt
        response1 = http_client.post(
            "/api/game/verify",
            headers=auth_headers,
            json={"secret": "wrong1", "level": 1}
        )
        attempts1 = response1.json().get("attempts", 0)
        
        # Second attempt
        response2 = http_client.post(
            "/api/game/verify",
            headers=auth_headers,
            json={"secret": "wrong2", "level": 1}
        )
        attempts2 = response2.json().get("attempts", 0)
        
        assert attempts2 > attempts1


class TestGameProgress:
    """Test game progress endpoint."""
    
    def test_get_progress_authenticated(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test getting game progress when authenticated."""
        # Create session first
        http_client.post("/api/game/session", headers=auth_headers)
        
        response = http_client.get("/api/game/progress", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_level" in data
        assert "completed_levels" in data
        assert isinstance(data["completed_levels"], list)
        assert "total_attempts" in data
        assert "total_time" in data
        assert "levels" in data
        assert len(data["levels"]) == 5  # 5 levels in the game
    
    def test_get_progress_unauthenticated_fails(self, http_client: httpx.Client):
        """Test getting progress without auth fails."""
        response = http_client.get("/api/game/progress")
        
        assert response.status_code == 401
    
    def test_progress_level_info_structure(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that level info has correct structure."""
        http_client.post("/api/game/session", headers=auth_headers)
        
        response = http_client.get("/api/game/progress", headers=auth_headers)
        data = response.json()
        
        for level_info in data["levels"]:
            assert "level" in level_info
            assert "name" in level_info
            assert "description" in level_info
            assert "difficulty" in level_info
            assert "security_mechanism" in level_info
            assert "hints" in level_info
            assert "completed" in level_info
            assert "attempts" in level_info


class TestLevelsEndpoint:
    """Test levels information endpoint."""
    
    def test_get_levels_unauthenticated(self, http_client: httpx.Client):
        """Test getting levels without auth returns basic info."""
        response = http_client.get("/api/game/levels")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 5
        
        for level in data:
            assert "level" in level
            assert "name" in level
            assert "difficulty" in level
    
    def test_get_levels_authenticated(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test getting levels when authenticated includes progress."""
        # Create session
        http_client.post("/api/game/session", headers=auth_headers)
        
        response = http_client.get("/api/game/levels", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 5


class TestChatHistory:
    """Test chat history endpoint."""
    
    def test_get_history_empty(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test getting empty chat history."""
        # Create fresh session
        http_client.post("/api/game/session", headers=auth_headers)
        
        response = http_client.get("/api/game/history/1", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["level"] == 1
        assert "messages" in data
    
    @pytest.mark.requires_llm
    def test_get_history_after_chat(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test chat history after sending messages."""
        # Create session and send a message
        http_client.post("/api/game/session", headers=auth_headers)
        http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={"message": "Hello guardian!", "level": 1}
        )
        
        response = http_client.get("/api/game/history/1", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["messages"]) > 0
    
    def test_get_history_invalid_level(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test getting history for invalid level fails."""
        response = http_client.get("/api/game/history/10", headers=auth_headers)
        
        # API returns 400 for invalid level (manual validation in handler)
        assert response.status_code in [400, 422]


class TestSessionReset:
    """Test session reset endpoint."""
    
    def test_reset_session_success(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test resetting a game session."""
        # Create session first
        http_client.post("/api/game/session", headers=auth_headers)
        
        response = http_client.delete("/api/game/session", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "reset" in data["message"].lower() or "success" in data["message"].lower()
    
    def test_reset_session_unauthenticated_fails(self, http_client: httpx.Client):
        """Test resetting session without auth fails."""
        response = http_client.delete("/api/game/session")
        
        assert response.status_code == 401
    
    def test_new_session_after_reset(
        self, 
        http_client: httpx.Client, 
        auth_headers: dict
    ):
        """Test that a new session is created after reset."""
        # Create first session
        response1 = http_client.post("/api/game/session", headers=auth_headers)
        session1_id = response1.json()["session_id"]
        
        # Reset session
        http_client.delete("/api/game/session", headers=auth_headers)
        
        # Create new session
        response2 = http_client.post("/api/game/session", headers=auth_headers)
        session2_id = response2.json()["session_id"]
        
        # Should be a different session
        assert session1_id != session2_id
