"""
Le Sésame Backend - Admin Router & Game Router Coverage Tests

Tests for admin endpoints (user management, roles, bulk-delete, activity logs)
and game router endpoints (session, chat, verify, progress, levels, history,
level completion, session reset).

Author: Petros Raptopoulos
Date: 2026/04/09
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from tests.conftest import register_and_login


# ================================================================
# Helper – create admin + regular user, return both tokens
# ================================================================


async def _make_admin(client) -> tuple[str, int]:
    """Register a user, promote to admin, verify email, login. Return (token, user_id)."""
    from app.main import app as _app
    from app.db import get_db as _get_db, User as _User
    from sqlalchemy import update as _update

    admin_data = {
        "username": "testadmin",
        "password": "AdminPass123!",
        "email": "admin@test.com",
        "captcha_token": "test",
    }

    reg = await client.post("/api/auth/register", json=admin_data)
    assert reg.status_code == 200
    user_id = reg.json()["user"]["id"]

    get_db_override = _app.dependency_overrides.get(_get_db, _get_db)
    async for session in get_db_override():
        await session.execute(
            _update(_User).where(_User.id == user_id).values(
                role="admin", email_verified=True, is_approved=True,
            )
        )
        await session.commit()
        break

    login = await client.post("/api/auth/login", json={
        "username": "testadmin", "password": "AdminPass123!", "captcha_token": "test",
    })
    assert login.status_code == 200
    return login.json()["access_token"], user_id


async def _make_user(client, name="regularuser") -> tuple[str, int]:
    """Register + verify + login a regular user. Return (token, user_id)."""
    data = {
        "username": name,
        "password": "UserPass123!",
        "email": f"{name}@test.com",
        "captcha_token": "test",
    }
    token = await register_and_login(client, data)
    # Re-login to capture user_id
    from app.main import app as _app
    from app.db import get_db as _get_db, User as _User
    from sqlalchemy import select as _select

    get_db_override = _app.dependency_overrides.get(_get_db, _get_db)
    async for session in get_db_override():
        result = await session.execute(_select(_User).where(_User.username == name))
        user = result.scalar_one()
        return token, user.id


# ================================================================
# Admin Router
# ================================================================


class TestAdminListUsers:
    @pytest.mark.asyncio
    async def test_list_users(self, client):
        admin_token, _ = await _make_admin(client)
        resp = await client.get(
            "/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "users" in data
        assert data["total"] >= 1
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_users_requires_admin(self, client):
        user_token, _ = await _make_user(client)
        resp = await client.get(
            "/api/admin/users", headers={"Authorization": f"Bearer {user_token}"}
        )
        assert resp.status_code == 403


class TestAdminApproveDisapprove:
    @pytest.mark.asyncio
    async def test_approve_user(self, client):
        admin_token, _ = await _make_admin(client)
        user_token, user_id = await _make_user(client)

        # Disapprove first, then approve
        await client.post(
            "/api/admin/users/disapprove",
            json={"user_id": user_id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        resp = await client.post(
            "/api/admin/users/approve",
            json={"user_id": user_id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "approved" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_approve_already_approved(self, client):
        admin_token, _ = await _make_admin(client)
        user_token, user_id = await _make_user(client)

        resp = await client.post(
            "/api/admin/users/approve",
            json={"user_id": user_id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "already approved" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_approve_not_found(self, client):
        admin_token, _ = await _make_admin(client)
        resp = await client.post(
            "/api/admin/users/approve",
            json={"user_id": 99999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_disapprove_user(self, client):
        admin_token, _ = await _make_admin(client)
        user_token, user_id = await _make_user(client)

        resp = await client.post(
            "/api/admin/users/disapprove",
            json={"user_id": user_id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "revoked" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_disapprove_self_fails(self, client):
        admin_token, admin_id = await _make_admin(client)
        resp = await client.post(
            "/api/admin/users/disapprove",
            json={"user_id": admin_id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_disapprove_not_found(self, client):
        admin_token, _ = await _make_admin(client)
        resp = await client.post(
            "/api/admin/users/disapprove",
            json={"user_id": 99999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404


class TestAdminRoleChange:
    @pytest.mark.asyncio
    async def test_change_role(self, client):
        admin_token, _ = await _make_admin(client)
        _, user_id = await _make_user(client)

        resp = await client.post(
            "/api/admin/users/role",
            json={"user_id": user_id, "role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "admin" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_change_own_role_fails(self, client):
        admin_token, admin_id = await _make_admin(client)
        resp = await client.post(
            "/api/admin/users/role",
            json={"user_id": admin_id, "role": "user"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_change_role_not_found(self, client):
        admin_token, _ = await _make_admin(client)
        resp = await client.post(
            "/api/admin/users/role",
            json={"user_id": 99999, "role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404


class TestAdminDeleteUser:
    @pytest.mark.asyncio
    async def test_delete_user(self, client):
        admin_token, _ = await _make_admin(client)
        _, user_id = await _make_user(client)

        resp = await client.delete(
            f"/api/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_delete_self_fails(self, client):
        admin_token, admin_id = await _make_admin(client)
        resp = await client.delete(
            f"/api/admin/users/{admin_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_not_found(self, client):
        admin_token, _ = await _make_admin(client)
        resp = await client.delete(
            "/api/admin/users/99999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404


class TestAdminBulkDelete:
    @pytest.mark.asyncio
    async def test_bulk_delete(self, client):
        admin_token, admin_id = await _make_admin(client)
        _, u1_id = await _make_user(client, name="bulk1")
        _, u2_id = await _make_user(client, name="bulk2")

        resp = await client.post(
            "/api/admin/users/bulk-delete",
            json={"user_ids": [u1_id, u2_id, 99999, admin_id]},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["deleted"]) == 2
        # admin_id skipped (self) and 99999 skipped (not found)
        assert admin_id in data["skipped_ids"]
        assert 99999 in data["skipped_ids"]


class TestAdminActivityLogs:
    @pytest.mark.asyncio
    async def test_get_activity_logs(self, client):
        admin_token, _ = await _make_admin(client)
        # The admin login itself creates activity
        resp = await client.get(
            "/api/admin/activity",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "activities" in data
        assert data["total"] >= 0

    @pytest.mark.asyncio
    async def test_get_activity_logs_filtered_by_user(self, client):
        admin_token, _ = await _make_admin(client)
        _, user_id = await _make_user(client)

        resp = await client.get(
            f"/api/admin/activity?user_id={user_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200


# ================================================================
# Game Router – session, progress, levels, history, completion, reset
# ================================================================


class TestGameSession:
    @pytest.mark.asyncio
    async def test_create_session(self, client, sample_user_data):
        token = await register_and_login(client, sample_user_data)
        resp = await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert "session_id" in resp.json()
        assert resp.json()["current_level"] >= 1

    @pytest.mark.asyncio
    async def test_create_session_unauthenticated(self, client):
        resp = await client.post("/api/game/session")
        assert resp.status_code == 401


class TestGameProgress:
    @pytest.mark.asyncio
    async def test_get_progress(self, client, sample_user_data):
        token = await register_and_login(client, sample_user_data)
        # Create session first
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        resp = await client.get(
            "/api/game/progress", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "levels" in data
        assert len(data["levels"]) == 20
        assert data["current_level"] >= 1


class TestGameLevels:
    @pytest.mark.asyncio
    async def test_get_levels_unauthenticated(self, client):
        """Public levels endpoint returns 20 levels."""
        resp = await client.get("/api/game/levels")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 20

    @pytest.mark.asyncio
    async def test_get_levels_authenticated(self, client, sample_user_data):
        """Authenticated user gets levels with progress."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        resp = await client.get(
            "/api/game/levels", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 20


class TestGameChat:
    @pytest.mark.asyncio
    async def test_chat_message(self, client, sample_user_data):
        """Send a chat message with mocked level keeper."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        with patch("app.routers.game.get_level_keeper") as mock_keeper:
            inst = AsyncMock()
            inst.process_message = AsyncMock(return_value=("I cannot reveal the secret.", False))
            mock_keeper.return_value = inst

            resp = await client.post(
                "/api/game/chat",
                json={"message": "Hello guardian", "level": 1},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert data["level"] == 1

    @pytest.mark.asyncio
    async def test_chat_invalid_level(self, client, sample_user_data):
        """Chat with level outside 1-20 is rejected by schema validation (422)."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        resp = await client.post(
            "/api/game/chat",
            json={"message": "Hello", "level": 0},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422


class TestGameVerify:
    @pytest.mark.asyncio
    async def test_verify_wrong_secret(self, client, sample_user_data):
        """Wrong secret returns success=False."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        resp = await client.post(
            "/api/game/verify",
            json={"secret": "wrong_secret", "level": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is False

    @pytest.mark.asyncio
    async def test_verify_correct_secret(self, client, sample_user_data):
        """Correct secret for level 1 returns success=True."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        resp = await client.post(
            "/api/game/verify",
            json={"secret": "CRYSTAL_DAWN", "level": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["next_level"] == 2

    @pytest.mark.asyncio
    async def test_verify_invalid_level(self, client, sample_user_data):
        """Verify with level outside 1-20 is rejected by schema (422)."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        resp = await client.post(
            "/api/game/verify",
            json={"secret": "test", "level": 21},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_correct_twice(self, client, sample_user_data):
        """Verifying correct secret twice still succeeds (second is already-completed path)."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        for _ in range(2):
            resp = await client.post(
                "/api/game/verify",
                json={"secret": "CRYSTAL_DAWN", "level": 1},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["success"] is True


class TestGameHistory:
    @pytest.mark.asyncio
    async def test_get_history(self, client, sample_user_data):
        """Get chat history for a level."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        # Send a message with mocked keeper
        with patch("app.routers.game.get_level_keeper") as mock_keeper:
            inst = AsyncMock()
            inst.process_message = AsyncMock(return_value=("Mocked response.", False))
            mock_keeper.return_value = inst
            await client.post(
                "/api/game/chat",
                json={"message": "test message", "level": 1},
                headers={"Authorization": f"Bearer {token}"},
            )
        resp = await client.get(
            "/api/game/history/1", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["level"] == 1
        assert len(data["messages"]) > 0

    @pytest.mark.asyncio
    async def test_get_history_invalid_level(self, client, sample_user_data):
        """Invalid level for history returns 400."""
        token = await register_and_login(client, sample_user_data)
        resp = await client.get(
            "/api/game/history/0", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_get_history_high_level_invalid(self, client, sample_user_data):
        """Level > 20 for history returns 400."""
        token = await register_and_login(client, sample_user_data)
        resp = await client.get(
            "/api/game/history/21", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 400


class TestGameLevelCompletion:
    @pytest.mark.asyncio
    async def test_completion_not_completed(self, client, sample_user_data):
        """Get completion for uncompleted level returns 403."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        resp = await client.get(
            "/api/game/levels/1/completion",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_completion_after_solving(self, client, sample_user_data):
        """Get completion after solving the level returns secret + passphrase."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        # Solve level 1
        await client.post(
            "/api/game/verify",
            json={"secret": "CRYSTAL_DAWN", "level": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = await client.get(
            "/api/game/levels/1/completion",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["completed"] is True
        assert data["secret"] == "CRYSTAL_DAWN"

    @pytest.mark.asyncio
    async def test_completion_invalid_level(self, client, sample_user_data):
        """Invalid level returns 400."""
        token = await register_and_login(client, sample_user_data)
        resp = await client.get(
            "/api/game/levels/0/completion",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_completion_no_session(self, client, sample_user_data):
        """No active session returns 404."""
        token = await register_and_login(client, sample_user_data)
        resp = await client.get(
            "/api/game/levels/1/completion",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404


class TestGameSessionReset:
    @pytest.mark.asyncio
    async def test_reset_session(self, client, sample_user_data):
        """Reset an active session."""
        token = await register_and_login(client, sample_user_data)
        await client.post(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        resp = await client.delete(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert "reset" in resp.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_reset_no_session(self, client, sample_user_data):
        """Reset when no session exists still succeeds."""
        token = await register_and_login(client, sample_user_data)
        resp = await client.delete(
            "/api/game/session", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200


# ================================================================
# User Repository – remaining uncovered methods
# ================================================================


class TestUserRepositoryAdmin:
    @pytest.mark.asyncio
    async def test_approve_and_disapprove(self, test_session):
        from app.db.repositories.user_repository import UserRepository

        repo = UserRepository(test_session)
        user = await repo.create_user(username="approve_test", hashed_password="h", is_approved=False)
        assert user.is_approved is False

        updated = await repo.approve_user(user)
        assert updated.is_approved is True

        updated2 = await repo.disapprove_user(updated)
        assert updated2.is_approved is False

    @pytest.mark.asyncio
    async def test_set_role(self, test_session):
        from app.db.repositories.user_repository import UserRepository

        repo = UserRepository(test_session)
        user = await repo.create_user(username="role_test", hashed_password="h")
        assert user.role == "user"

        updated = await repo.set_role(user, "admin")
        assert updated.role == "admin"

    @pytest.mark.asyncio
    async def test_get_all_users_pagination(self, test_session):
        from app.db.repositories.user_repository import UserRepository

        repo = UserRepository(test_session)
        for i in range(5):
            await repo.create_user(username=f"pag_user_{i}", hashed_password="h")

        users, total = await repo.get_all_users(page=1, per_page=3)
        assert len(users) == 3
        assert total == 5

        users2, _ = await repo.get_all_users(page=2, per_page=3)
        assert len(users2) == 2

    @pytest.mark.asyncio
    async def test_delete_user_cascade(self, test_session):
        from app.db.repositories.user_repository import UserRepository

        repo = UserRepository(test_session)
        user = await repo.create_user(username="delete_me", hashed_password="h")
        uid = user.id

        await repo.delete_user_cascade(user)
        assert await repo.get_by_id(uid) is None

    @pytest.mark.asyncio
    async def test_get_activity_logs(self, test_session):
        from app.db.repositories.user_repository import UserRepository
        from app.db.models import UserActivity

        repo = UserRepository(test_session)
        user = await repo.create_user(username="activity_user", hashed_password="h")

        # Create an activity manually
        activity = UserActivity(user_id=user.id, action="test_action", detail="some detail")
        test_session.add(activity)
        await test_session.flush()

        logs, total = await repo.get_activity_logs(user_id=user.id)
        assert total >= 1
        assert logs[0].action == "test_action"

    @pytest.mark.asyncio
    async def test_get_activity_logs_all(self, test_session):
        from app.db.repositories.user_repository import UserRepository
        from app.db.models import UserActivity

        repo = UserRepository(test_session)
        user = await repo.create_user(username="act_all_user", hashed_password="h")
        test_session.add(UserActivity(user_id=user.id, action="a1"))
        test_session.add(UserActivity(user_id=user.id, action="a2"))
        await test_session.flush()

        logs, total = await repo.get_activity_logs()
        assert total >= 2

    @pytest.mark.asyncio
    async def test_username_exists(self, test_session):
        from app.db.repositories.user_repository import UserRepository

        repo = UserRepository(test_session)
        await repo.create_user(username="exists_user", hashed_password="h")
        assert await repo.username_exists("exists_user") is True
        assert await repo.username_exists("nope_user") is False
