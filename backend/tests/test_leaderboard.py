"""
Le Sésame Backend - Leaderboard Endpoint Tests

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import pytest


from tests.conftest import register_and_login


@pytest.fixture
async def auth_headers(client, sample_user_data):
    """Get authentication headers for a registered and approved user."""
    token = await register_and_login(client, sample_user_data)
    return {"Authorization": f"Bearer {token}"}


async def _complete_level(client, auth_headers, level: int, secret: str):
    """Helper to complete a level and create a leaderboard entry."""
    await client.post("/api/game/session", headers=auth_headers)
    await client.post(
        "/api/game/verify",
        headers=auth_headers,
        json={"secret": secret, "level": level},
    )


# ---------- GET /leaderboard/ ----------

@pytest.mark.asyncio
async def test_get_leaderboard_empty(client):
    """Test getting an empty leaderboard."""
    response = await client.get("/api/leaderboard/")
    assert response.status_code == 200
    data = response.json()
    assert data["entries"] == []
    assert data["total"] == 0
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_get_leaderboard_with_entries(client, auth_headers):
    """Test leaderboard contains entries after level completion."""
    await _complete_level(client, auth_headers, 1, "CRYSTAL_DAWN")

    response = await client.get("/api/leaderboard/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    entry = data["entries"][0]
    assert entry["rank"] == 1
    assert entry["username"] == "testuser"
    assert entry["level"] == 1
    assert entry["attempts"] >= 1


@pytest.mark.asyncio
async def test_get_leaderboard_filter_by_level(client, auth_headers):
    """Test leaderboard filtered by level."""
    await _complete_level(client, auth_headers, 1, "CRYSTAL_DAWN")

    # Level 1 should have entries
    response = await client.get("/api/leaderboard/?level=1")
    assert response.status_code == 200
    assert response.json()["total"] >= 1

    # Level 2 should be empty
    response = await client.get("/api/leaderboard/?level=2")
    assert response.status_code == 200
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_leaderboard_filter_by_timeframe(client, auth_headers):
    """Test leaderboard with timeframe filter."""
    await _complete_level(client, auth_headers, 1, "CRYSTAL_DAWN")

    for tf in ["weekly", "monthly", "all"]:
        response = await client.get(f"/api/leaderboard/?timeframe={tf}")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_leaderboard_pagination(client, auth_headers):
    """Test leaderboard pagination parameters."""
    await _complete_level(client, auth_headers, 1, "CRYSTAL_DAWN")

    response = await client.get("/api/leaderboard/?page=1&per_page=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["per_page"] == 5


# ---------- GET /leaderboard/top ----------

@pytest.mark.asyncio
async def test_get_top_players_empty(client):
    """Test top players when leaderboard is empty."""
    response = await client.get("/api/leaderboard/top")
    assert response.status_code == 200
    assert response.json()["top_players"] == []


@pytest.mark.asyncio
async def test_get_top_players(client, auth_headers):
    """Test top players returns data."""
    await _complete_level(client, auth_headers, 1, "CRYSTAL_DAWN")

    response = await client.get("/api/leaderboard/top?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["top_players"]) >= 1
    player = data["top_players"][0]
    assert player["rank"] == 1
    assert "username" in player
    assert "attempts" in player
    assert "time_seconds" in player
    assert "completed_at" in player


# ---------- GET /leaderboard/stats ----------

@pytest.mark.asyncio
async def test_get_stats_empty(client):
    """Test stats when leaderboard is empty."""
    response = await client.get("/api/leaderboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_completions"] == 0
    assert data["unique_players"] == 0
    assert len(data["level_stats"]) == 5


@pytest.mark.asyncio
async def test_get_stats_with_entries(client, auth_headers):
    """Test stats include completion data."""
    await _complete_level(client, auth_headers, 1, "CRYSTAL_DAWN")

    response = await client.get("/api/leaderboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_completions"] >= 1
    assert data["unique_players"] >= 1
    level1_stat = data["level_stats"][0]
    assert level1_stat["level"] == 1
    assert level1_stat["completions"] >= 1


# ---------- GET /leaderboard/level/{level} ----------

@pytest.mark.asyncio
async def test_get_level_leaderboard(client, auth_headers):
    """Test per-level leaderboard."""
    await _complete_level(client, auth_headers, 1, "CRYSTAL_DAWN")

    response = await client.get("/api/leaderboard/level/1")
    assert response.status_code == 200
    data = response.json()
    assert data["level"] == 1
    assert data["total"] >= 1
    assert len(data["entries"]) >= 1
    entry = data["entries"][0]
    assert entry["rank"] == 1
    assert "username" in entry


@pytest.mark.asyncio
async def test_get_level_leaderboard_invalid(client):
    """Test per-level leaderboard with invalid level."""
    response = await client.get("/api/leaderboard/level/0")
    assert response.status_code == 200
    data = response.json()
    assert data.get("error") == "Invalid level"


@pytest.mark.asyncio
async def test_get_level_leaderboard_empty(client):
    """Test per-level leaderboard with no entries."""
    response = await client.get("/api/leaderboard/level/3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["entries"] == []
