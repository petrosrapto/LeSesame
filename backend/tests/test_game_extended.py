"""
Le Sésame Backend - Extended Game Endpoint Tests

Tests for game router endpoints not covered by test_game.py:
  - verify correct passphrase
  - level completion endpoint
  - session reset
  - progress with completed levels
  - chat history for invalid level
  - levels with authenticated user that has progress

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


from tests.conftest import register_and_login


@pytest.fixture
async def auth_headers(client, sample_user_data):
    """Get authentication headers for a registered and approved user."""
    token = await register_and_login(client, sample_user_data)
    return {"Authorization": f"Bearer {token}"}


# ---------- verify endpoint ----------

@pytest.mark.asyncio
async def test_verify_secret_correct(client, auth_headers):
    """Test verifying the correct secret succeeds."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "CRYSTAL_DAWN", "level": 1},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["level"] == 1
    assert data["secret"] == "CRYSTAL_DAWN"
    assert data["next_level"] == 2
    assert data["attempts"] >= 1
    assert data["time_spent"] is not None


@pytest.mark.asyncio
async def test_verify_secret_correct_case_insensitive(client, auth_headers):
    """Test that verification is case-insensitive."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "crystal_dawn", "level": 1},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_verify_secret_invalid_level(client, auth_headers):
    """Test verifying with an invalid level."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "whatever", "level": 0},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_verify_last_level_no_next(client, auth_headers):
    """Test completing level 20 returns next_level=None."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "NULL_THRONE", "level": 20},
    )
    data = response.json()
    assert data["success"] is True
    assert data["next_level"] is None


@pytest.mark.asyncio
async def test_verify_already_completed_level(client, auth_headers):
    """Test completing the same level twice still returns success."""
    await client.post("/api/game/session", headers=auth_headers)

    # First completion
    await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "CRYSTAL_DAWN", "level": 1},
    )
    # Second completion
    response = await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "CRYSTAL_DAWN", "level": 1},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_verify_unauthenticated(client):
    """Test verify without auth returns 401."""
    response = await client.post(
        "/api/game/verify",
        json={"secret": "test", "level": 1},
    )
    assert response.status_code == 401


# ---------- level completion endpoint ----------

@pytest.mark.asyncio
async def test_get_level_completion_after_complete(client, auth_headers):
    """Test fetching completion details for a completed level."""
    await client.post("/api/game/session", headers=auth_headers)

    # Complete level 1
    await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "CRYSTAL_DAWN", "level": 1},
    )

    response = await client.get(
        "/api/game/levels/1/completion",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["level"] == 1
    assert data["secret"] == "CRYSTAL_DAWN"
    assert data["passphrase"] == "open sesame"
    assert data["completed"] is True


@pytest.mark.asyncio
async def test_get_level_completion_not_completed(client, auth_headers):
    """Test fetching completion for an incomplete level returns 403."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.get(
        "/api/game/levels/1/completion",
        headers=auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_level_completion_no_session(client, auth_headers):
    """Test fetching completion with no active session returns 404."""
    response = await client.get(
        "/api/game/levels/1/completion",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_level_completion_invalid_level(client, auth_headers):
    """Test fetching completion for invalid level returns 400."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.get(
        "/api/game/levels/0/completion",
        headers=auth_headers,
    )
    assert response.status_code == 400

    response = await client.get(
        "/api/game/levels/21/completion",
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------- session endpoints ----------

@pytest.mark.asyncio
async def test_reset_session(client, auth_headers):
    """Test resetting a game session."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.delete("/api/game/session", headers=auth_headers)
    assert response.status_code == 200
    assert "reset" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_reset_session_no_active(client, auth_headers):
    """Test resetting when no session exists still returns 200."""
    response = await client.delete("/api/game/session", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_session_idempotent(client, auth_headers):
    """Test creating a session twice returns the same session."""
    r1 = await client.post("/api/game/session", headers=auth_headers)
    r2 = await client.post("/api/game/session", headers=auth_headers)
    assert r1.json()["session_id"] == r2.json()["session_id"]


# ---------- progress endpoint ----------

@pytest.mark.asyncio
async def test_progress_with_completed_levels(client, auth_headers):
    """Test progress includes completed level data."""
    await client.post("/api/game/session", headers=auth_headers)

    # Complete level 1
    await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "CRYSTAL_DAWN", "level": 1},
    )

    response = await client.get("/api/game/progress", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert 1 in data["completed_levels"]
    assert data["total_attempts"] >= 1
    assert data["total_time"] >= 0

    # Verify level info
    level1 = next(l for l in data["levels"] if l["level"] == 1)
    assert level1["completed"] is True
    assert level1["attempts"] >= 1
    assert level1["best_time"] is not None


@pytest.mark.asyncio
async def test_progress_unauthenticated(client):
    """Test progress without auth returns 401."""
    response = await client.get("/api/game/progress")
    assert response.status_code == 401


# ---------- levels endpoint ----------

@pytest.mark.asyncio
async def test_get_levels_with_progress(client, auth_headers):
    """Test levels endpoint includes user progress."""
    await client.post("/api/game/session", headers=auth_headers)

    # Complete a level
    await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": "CRYSTAL_DAWN", "level": 1},
    )

    response = await client.get("/api/game/levels", headers=auth_headers)
    data = response.json()
    level1 = next(l for l in data if l["level"] == 1)
    assert level1["completed"] is True


# ---------- history endpoint ----------

@pytest.mark.asyncio
async def test_get_history_invalid_level(client, auth_headers):
    """Test fetching history for invalid level returns 400."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.get("/api/game/history/0", headers=auth_headers)
    assert response.status_code == 400

    response = await client.get("/api/game/history/21", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_history_empty(client, auth_headers):
    """Test fetching history with no messages returns empty list."""
    await client.post("/api/game/session", headers=auth_headers)

    response = await client.get("/api/game/history/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["messages"] == []


# ---------- chat endpoint edge cases ----------

@pytest.mark.asyncio
async def test_chat_unauthenticated(client):
    """Test sending chat without auth returns 401."""
    response = await client.post(
        "/api/game/chat",
        json={"message": "Hello", "level": 1},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_with_model_config(client, auth_headers):
    """Test sending chat with model_config override."""
    await client.post("/api/game/session", headers=auth_headers)

    with patch("app.routers.game.get_level_keeper") as mock_keeper:
        mock_instance = AsyncMock()
        mock_instance.process_message = AsyncMock(
            return_value=("Test response", False)
        )
        mock_keeper.return_value = mock_instance

        response = await client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={
                "message": "Hello",
                "level": 1,
                "model_config": {
                    "provider": "openai",
                    "model_id": "gpt-4o",
                },
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Test response"
    assert data["messages_count"] >= 1
