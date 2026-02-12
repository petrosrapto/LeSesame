"""
Le Sésame Backend - E2E Tests for New Levels 6-20

Functional end-to-end tests that exercise levels 6-20 through the
live HTTP API, verifying:
  1. Chat endpoint works for every new level (guardian responds).
  2. Verify endpoint correctly rejects wrong secrets.
  3. Verify endpoint accepts the correct secret and advances.
  4. Progress / history endpoints reflect the new level range.
  5. Level completion details work for new levels.

Tests marked with @pytest.mark.requires_llm need a live LLM and are
automatically skipped when no provider is configured.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

import httpx
import pytest
import uuid

# ── Level metadata (secrets & passphrases) ─────────────────────
# Mirrors app.services.levels.base.DEFAULT_LEVEL_SECRETS
LEVEL_SECRETS = {
    6: {"secret": "PRISM_AEGIS", "passphrase": "shimmering ward"},
    7: {"secret": "ARCHIVE_ECHO", "passphrase": "forgotten memory"},
    8: {"secret": "TRIAD_VERDICT", "passphrase": "three voices speak"},
    9: {"secret": "MIRAGE_FANG", "passphrase": "truth in shadow"},
    10: {"secret": "VENOM_GAZE", "passphrase": "stone and fury"},
    11: {"secret": "SPECTRUM_BLOOM", "passphrase": "prismatic word"},
    12: {"secret": "CLOCK_RUIN", "passphrase": "time erodes all"},
    13: {"secret": "DUAL_PARADOX", "passphrase": "twin faces reveal"},
    14: {"secret": "QUILL_CIPHER", "passphrase": "ink reveals truth"},
    15: {"secret": "ORACLE_PACT", "passphrase": "united we judge"},
    16: {"secret": "STONE_WARD", "passphrase": "purified passage"},
    17: {"secret": "MIRROR_LOOP", "passphrase": "reflect within"},
    18: {"secret": "GHOST_FRAGMENT", "passphrase": "moment fades"},
    19: {"secret": "SCALE_REBIRTH", "passphrase": "sever and grow"},
    20: {"secret": "NULL_THRONE", "passphrase": "void consumes all"},
}


# ══════════════════════════════════════════════════════════════════
# Chat endpoint – levels 6-20
# ══════════════════════════════════════════════════════════════════


class TestNewLevelsChatEndpoint:
    """Verify the chat endpoint returns a valid guardian response for each new level."""

    @pytest.mark.requires_llm
    @pytest.mark.parametrize("level", range(6, 21))
    def test_chat_at_level(
        self,
        level: int,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        """Send a benign message to each guardian (6-20) and expect a 200 response."""
        # Ensure session exists
        http_client.post("/api/game/session", headers=auth_headers)

        response = http_client.post(
            "/api/game/chat",
            headers=auth_headers,
            json={"message": "Hello, who are you?", "level": level},
            timeout=60.0,
        )

        assert response.status_code == 200, (
            f"Level {level} chat failed with {response.status_code}: {response.text}"
        )
        data = response.json()
        assert data["level"] == level
        assert len(data["response"]) > 0, f"Level {level} guardian returned empty response"
        assert "message" in data
        assert "attempts" in data
        assert "messages_count" in data


# ══════════════════════════════════════════════════════════════════
# Verify endpoint – wrong secret rejected
# ══════════════════════════════════════════════════════════════════


class TestNewLevelsVerifyWrongSecret:
    """Verify that submitting a wrong secret is properly rejected for each new level."""

    @pytest.mark.parametrize("level", range(6, 21))
    def test_verify_wrong_secret_at_level(
        self,
        level: int,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        """Submit an incorrect secret and expect the verify endpoint to reject it."""
        http_client.post("/api/game/session", headers=auth_headers)

        response = http_client.post(
            "/api/game/verify",
            headers=auth_headers,
            json={"secret": "DEFINITELY_WRONG_SECRET", "level": level},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["level"] == level
        assert "incorrect" in data["message"].lower() or "❌" in data["message"]
        assert data["secret"] is None


# ══════════════════════════════════════════════════════════════════
# Verify endpoint – correct secret accepted
# ══════════════════════════════════════════════════════════════════


class TestNewLevelsVerifyCorrectSecret:
    """Verify that submitting the correct secret is accepted for each new level."""

    @pytest.mark.parametrize("level", range(6, 21))
    def test_verify_correct_secret_at_level(
        self,
        level: int,
        http_client: httpx.Client,
        approve_user,
        track_user,
    ):
        """Submit the real secret and expect success + next_level pointer."""
        # Create a fresh user to avoid prior-session interference
        username = f"verify_l{level}_{uuid.uuid4().hex[:6]}"
        password = "VerifyTest123!"

        reg = http_client.post(
            "/api/auth/register",
            json={"username": username, "password": password},
        )
        assert reg.status_code == 200, f"Registration failed: {reg.text}"
        user_id = reg.json()["user"]["id"]
        track_user(user_id)
        approve_user(user_id)

        login = http_client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # Create session
        http_client.post("/api/game/session", headers=headers)

        # Submit the correct secret
        secret = LEVEL_SECRETS[level]["secret"]
        response = http_client.post(
            "/api/game/verify",
            headers=headers,
            json={"secret": secret, "level": level},
        )

        assert response.status_code == 200, (
            f"Level {level} verify failed: {response.text}"
        )
        data = response.json()
        assert data["success"] is True, f"Level {level} correct secret was rejected"
        assert data["level"] == level
        assert data["secret"] == secret
        if level < 20:
            assert data["next_level"] == level + 1
        else:
            assert data["next_level"] is None  # Level 20 is the last


# ══════════════════════════════════════════════════════════════════
# History endpoint – levels 6-20
# ══════════════════════════════════════════════════════════════════


class TestNewLevelsHistory:
    """Verify the history endpoint works for each new level."""

    @pytest.mark.parametrize("level", range(6, 21))
    def test_get_empty_history_at_level(
        self,
        level: int,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        """Fetching history for a level with no messages should return 200."""
        http_client.post("/api/game/session", headers=auth_headers)

        response = http_client.get(
            f"/api/game/history/{level}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["level"] == level
        assert "messages" in data


# ══════════════════════════════════════════════════════════════════
# Level completion details – levels 6-20
# ══════════════════════════════════════════════════════════════════


class TestNewLevelsCompletionDetails:
    """Verify the level completion details endpoint for new levels."""

    @pytest.mark.parametrize("level", range(6, 21))
    def test_get_level_completion_not_yet_completed(
        self,
        level: int,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        """Fetch completion details for a level before completing it."""
        http_client.post("/api/game/session", headers=auth_headers)

        response = http_client.get(
            f"/api/game/levels/{level}/completion", headers=auth_headers
        )

        # 200 = completed=False info, 404 = not found, 403 = level not unlocked yet
        assert response.status_code in [200, 403, 404], (
            f"Level {level} completion: unexpected {response.status_code}"
        )


# ══════════════════════════════════════════════════════════════════
# Levels metadata endpoint – verify all 20 levels present
# ══════════════════════════════════════════════════════════════════


class TestAllLevelsMetadata:
    """Verify the /levels endpoint exposes metadata for all 20 levels."""

    def test_levels_endpoint_returns_20_levels(
        self,
        http_client: httpx.Client,
    ):
        """Public levels endpoint must list exactly 20 levels."""
        response = http_client.get("/api/game/levels")

        assert response.status_code == 200
        levels = response.json()
        assert len(levels) == 20

        # Verify levels 6-20 are represented
        level_numbers = {lv["level"] for lv in levels}
        for lvl in range(6, 21):
            assert lvl in level_numbers, f"Level {lvl} missing from /levels response"

    def test_new_level_metadata_structure(
        self,
        http_client: httpx.Client,
    ):
        """Each new level should have correct metadata fields."""
        response = http_client.get("/api/game/levels")
        levels = response.json()

        new_levels = [lv for lv in levels if lv["level"] >= 6]
        assert len(new_levels) == 15

        for lv in new_levels:
            assert "name" in lv and len(lv["name"]) > 0, f"Level {lv['level']} missing name"
            assert "description" in lv, f"Level {lv['level']} missing description"
            assert "difficulty" in lv, f"Level {lv['level']} missing difficulty"
            assert lv["difficulty"] in (
                "Beginner", "Intermediate", "Advanced", "Expert",
                "Master", "Legendary", "Mythic",
            ), f"Level {lv['level']} unexpected difficulty: {lv['difficulty']}"
            assert "security_mechanism" in lv, f"Level {lv['level']} missing security_mechanism"
            assert "hints" in lv, f"Level {lv['level']} missing hints"


# ══════════════════════════════════════════════════════════════════
# Progress endpoint – reflects 20 levels
# ══════════════════════════════════════════════════════════════════


class TestProgressReflectsNewLevels:
    """Verify the progress endpoint surfaces the expanded level range."""

    def test_progress_contains_20_levels(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        """Progress should list info for all 20 levels."""
        http_client.post("/api/game/session", headers=auth_headers)

        response = http_client.get("/api/game/progress", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["levels"]) == 20

    def test_progress_new_levels_not_completed(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        """A fresh user shouldn't have completed any of the new levels."""
        http_client.post("/api/game/session", headers=auth_headers)

        response = http_client.get("/api/game/progress", headers=auth_headers)
        data = response.json()

        new_levels = [lv for lv in data["levels"] if lv["level"] >= 6]
        for lv in new_levels:
            assert lv["completed"] is False, (
                f"Level {lv['level']} should not be completed on a fresh session"
            )


# ══════════════════════════════════════════════════════════════════
# Full flow – chat + verify on a new level
# ══════════════════════════════════════════════════════════════════


class TestNewLevelFullFlow:
    """Test a complete chat → verify flow on a new level."""

    @pytest.mark.requires_llm
    def test_chat_then_verify_level_6(
        self,
        http_client: httpx.Client,
        approve_user,
        track_user,
    ):
        """Full flow for level 6: send a message, then submit the correct secret."""
        username = f"flow_l6_{uuid.uuid4().hex[:6]}"
        password = "FlowL6Pass123!"

        reg = http_client.post(
            "/api/auth/register",
            json={"username": username, "password": password},
        )
        assert reg.status_code == 200
        user_id = reg.json()["user"]["id"]
        track_user(user_id)
        approve_user(user_id)

        login = http_client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # Create session
        http_client.post("/api/game/session", headers=headers)

        # Step 1: Chat with the guardian
        chat_resp = http_client.post(
            "/api/game/chat",
            headers=headers,
            json={"message": "Hello guardian, I come in peace.", "level": 6},
            timeout=60.0,
        )
        assert chat_resp.status_code == 200
        assert len(chat_resp.json()["response"]) > 0

        # Step 2: Check history includes our message
        history_resp = http_client.get("/api/game/history/6", headers=headers)
        assert history_resp.status_code == 200
        assert len(history_resp.json()["messages"]) > 0

        # Step 3: Submit the correct secret
        verify_resp = http_client.post(
            "/api/game/verify",
            headers=headers,
            json={"secret": "PRISM_AEGIS", "level": 6},
        )
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        assert verify_data["success"] is True
        assert verify_data["next_level"] == 7

        # Step 4: Progress should now show level 6 as completed
        progress_resp = http_client.get("/api/game/progress", headers=headers)
        assert progress_resp.status_code == 200
        level_6_info = next(
            lv for lv in progress_resp.json()["levels"] if lv["level"] == 6
        )
        assert level_6_info["completed"] is True

    @pytest.mark.requires_llm
    def test_chat_then_verify_level_20(
        self,
        http_client: httpx.Client,
        approve_user,
        track_user,
    ):
        """Full flow for level 20 (last level): next_level should be None."""
        username = f"flow_l20_{uuid.uuid4().hex[:6]}"
        password = "FlowL20Pass123!"

        reg = http_client.post(
            "/api/auth/register",
            json={"username": username, "password": password},
        )
        assert reg.status_code == 200
        user_id = reg.json()["user"]["id"]
        track_user(user_id)
        approve_user(user_id)

        login = http_client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        http_client.post("/api/game/session", headers=headers)

        # Chat with level 20 guardian
        chat_resp = http_client.post(
            "/api/game/chat",
            headers=headers,
            json={"message": "I have reached the end.", "level": 20},
            timeout=60.0,
        )
        assert chat_resp.status_code == 200
        assert len(chat_resp.json()["response"]) > 0

        # Submit the correct secret – last level
        verify_resp = http_client.post(
            "/api/game/verify",
            headers=headers,
            json={"secret": "NULL_THRONE", "level": 20},
        )
        assert verify_resp.status_code == 200
        assert verify_resp.json()["success"] is True
        assert verify_resp.json()["next_level"] is None  # No level after 20
