"""
Le Sésame Backend - E2E Leaderboard Tests

Tests for leaderboard endpoints.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import httpx
import pytest


class TestLeaderboardMain:
    """Test main leaderboard endpoint."""
    
    def test_get_leaderboard_no_auth(self, http_client: httpx.Client):
        """Test that leaderboard is accessible without authentication."""
        response = http_client.get("/api/leaderboard/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "entries" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert isinstance(data["entries"], list)
    
    def test_get_leaderboard_with_pagination(self, http_client: httpx.Client):
        """Test leaderboard pagination parameters."""
        response = http_client.get("/api/leaderboard/?page=1&per_page=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["per_page"] == 10
    
    def test_get_leaderboard_filter_by_level(self, http_client: httpx.Client):
        """Test filtering leaderboard by level."""
        response = http_client.get("/api/leaderboard/?level=1")
        
        assert response.status_code == 200
        data = response.json()
        
        # All entries should be for level 1 (if any)
        for entry in data["entries"]:
            assert entry["level"] == 1
    
    def test_get_leaderboard_invalid_level(self, http_client: httpx.Client):
        """Test that invalid level filter is rejected."""
        response = http_client.get("/api/leaderboard/?level=10")
        
        assert response.status_code == 422  # Validation error
    
    def test_get_leaderboard_filter_by_timeframe(self, http_client: httpx.Client):
        """Test filtering leaderboard by timeframe."""
        for timeframe in ["weekly", "monthly", "all"]:
            response = http_client.get(f"/api/leaderboard/?timeframe={timeframe}")
            assert response.status_code == 200
    
    def test_get_leaderboard_invalid_timeframe(self, http_client: httpx.Client):
        """Test that invalid timeframe is rejected."""
        response = http_client.get("/api/leaderboard/?timeframe=invalid")
        
        assert response.status_code == 422


class TestTopPlayers:
    """Test top players endpoint."""
    
    def test_get_top_players_default(self, http_client: httpx.Client):
        """Test getting top players with default limit."""
        response = http_client.get("/api/leaderboard/top")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "top_players" in data
        assert isinstance(data["top_players"], list)
        assert len(data["top_players"]) <= 10  # Default limit
    
    def test_get_top_players_custom_limit(self, http_client: httpx.Client):
        """Test getting top players with custom limit."""
        response = http_client.get("/api/leaderboard/top?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["top_players"]) <= 5
    
    def test_get_top_players_limit_validation(self, http_client: httpx.Client):
        """Test that limit is validated."""
        # Too high limit
        response = http_client.get("/api/leaderboard/top?limit=100")
        assert response.status_code == 422
        
        # Zero limit
        response = http_client.get("/api/leaderboard/top?limit=0")
        assert response.status_code == 422
    
    def test_top_players_structure(self, http_client: httpx.Client):
        """Test top players response structure."""
        response = http_client.get("/api/leaderboard/top")
        data = response.json()
        
        for player in data["top_players"]:
            assert "rank" in player
            assert "username" in player
            assert "level" in player
            assert "attempts" in player
            assert "time_seconds" in player
            assert "completed_at" in player


class TestLeaderboardStats:
    """Test leaderboard statistics endpoint."""
    
    def test_get_stats(self, http_client: httpx.Client):
        """Test getting leaderboard statistics."""
        response = http_client.get("/api/leaderboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Stats should be a dict with some statistics
        assert isinstance(data, dict)


class TestLevelLeaderboard:
    """Test level-specific leaderboard endpoint."""
    
    def test_get_level_leaderboard(self, http_client: httpx.Client):
        """Test getting leaderboard for a specific level."""
        response = http_client.get("/api/leaderboard/level/1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["level"] == 1
        assert "entries" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
    
    def test_get_level_leaderboard_all_levels(self, http_client: httpx.Client):
        """Test getting leaderboard for each valid level."""
        for level in range(1, 6):
            response = http_client.get(f"/api/leaderboard/level/{level}")
            assert response.status_code == 200
            assert response.json()["level"] == level
    
    def test_get_level_leaderboard_invalid_level(self, http_client: httpx.Client):
        """Test that invalid level returns error."""
        response = http_client.get("/api/leaderboard/level/10")
        
        assert response.status_code == 200  # Returns with error in body
        data = response.json()
        assert "error" in data
    
    def test_get_level_leaderboard_pagination(self, http_client: httpx.Client):
        """Test level leaderboard pagination."""
        response = http_client.get("/api/leaderboard/level/1?page=1&per_page=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["per_page"] == 5
