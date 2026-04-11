"""
Le Sésame Backend - Extended Auth Tests

Unit tests for email verification, captcha service, Google OAuth,
user repository auth methods, and admin auth overrides.

Author: Petros Raptopoulos
Date: 2026/04/09
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock

from tests.conftest import register_and_login

from app.services.captcha import verify_recaptcha
from app.services.email import (
    generate_verification_token,
    verification_expiry,
    build_verification_url,
    _build_verification_email,
    send_verification_email,
)
from app.db.repositories.user_repository import UserRepository


# ================================================================
# Captcha Service
# ================================================================


class TestCaptchaService:
    """Tests for reCAPTCHA v3 server-side verification."""

    @pytest.mark.asyncio
    async def test_skip_when_not_configured(self):
        """When secret key is empty, verification is skipped (returns True)."""
        with patch("app.services.captcha.settings") as mock_settings:
            mock_settings.recaptcha_secret_key = ""
            result = await verify_recaptcha("any-token", expected_action="login")
        assert result is True

    @pytest.mark.asyncio
    async def test_success(self):
        """Valid token with high score passes."""
        with patch("app.services.captcha.settings") as mock_settings, \
             patch("app.services.captcha.httpx.AsyncClient") as MockClient:
            mock_settings.recaptcha_secret_key = "secret"
            mock_settings.recaptcha_score_threshold = 0.5
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"success": True, "score": 0.9, "action": "login"}
            ctx = AsyncMock()
            ctx.post = AsyncMock(return_value=mock_resp)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = ctx

            result = await verify_recaptcha("good-token", expected_action="login")
        assert result is True

    @pytest.mark.asyncio
    async def test_failure_not_success(self):
        """Google returns success=false."""
        with patch("app.services.captcha.settings") as mock_settings, \
             patch("app.services.captcha.httpx.AsyncClient") as MockClient:
            mock_settings.recaptcha_secret_key = "secret"
            mock_settings.recaptcha_score_threshold = 0.5
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"success": False, "error-codes": ["invalid-input"]}
            ctx = AsyncMock()
            ctx.post = AsyncMock(return_value=mock_resp)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = ctx

            result = await verify_recaptcha("bad-token")
        assert result is False

    @pytest.mark.asyncio
    async def test_failure_low_score(self):
        """Score below threshold → reject."""
        with patch("app.services.captcha.settings") as mock_settings, \
             patch("app.services.captcha.httpx.AsyncClient") as MockClient:
            mock_settings.recaptcha_secret_key = "secret"
            mock_settings.recaptcha_score_threshold = 0.5
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"success": True, "score": 0.1, "action": "login"}
            ctx = AsyncMock()
            ctx.post = AsyncMock(return_value=mock_resp)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = ctx

            result = await verify_recaptcha("low-score-token", expected_action="login")
        assert result is False

    @pytest.mark.asyncio
    async def test_failure_action_mismatch(self):
        """Action mismatch → reject."""
        with patch("app.services.captcha.settings") as mock_settings, \
             patch("app.services.captcha.httpx.AsyncClient") as MockClient:
            mock_settings.recaptcha_secret_key = "secret"
            mock_settings.recaptcha_score_threshold = 0.5
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"success": True, "score": 0.9, "action": "register"}
            ctx = AsyncMock()
            ctx.post = AsyncMock(return_value=mock_resp)
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = ctx

            result = await verify_recaptcha("token", expected_action="login")
        assert result is False

    @pytest.mark.asyncio
    async def test_network_error_returns_false(self):
        """Network exception → reject (fail closed)."""
        with patch("app.services.captcha.settings") as mock_settings, \
             patch("app.services.captcha.httpx.AsyncClient") as MockClient:
            mock_settings.recaptcha_secret_key = "secret"
            mock_settings.recaptcha_score_threshold = 0.5
            ctx = AsyncMock()
            ctx.post = AsyncMock(side_effect=Exception("timeout"))
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = ctx

            result = await verify_recaptcha("token", expected_action="login")
        assert result is False


# ================================================================
# Email Service
# ================================================================


class TestEmailService:
    """Tests for email verification helpers and sending."""

    def test_generate_verification_token_length(self):
        """Token should be a non-empty string."""
        token = generate_verification_token()
        assert isinstance(token, str)
        assert len(token) > 30

    def test_generate_verification_token_unique(self):
        """Two tokens should not collide."""
        t1 = generate_verification_token()
        t2 = generate_verification_token()
        assert t1 != t2

    def test_verification_expiry_is_future(self):
        """Expiry should be ~24h in the future."""
        exp = verification_expiry()
        now = datetime.utcnow()
        assert exp > now
        assert exp < now + timedelta(hours=25)

    def test_build_verification_url(self):
        """URL should contain the token and the frontend base."""
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.frontend_url = "https://example.com"
            url = build_verification_url("abc123")
        assert url == "https://example.com/verify-email?token=abc123"

    def test_build_verification_url_trailing_slash(self):
        """Trailing slash on frontend_url should be stripped."""
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.frontend_url = "https://example.com/"
            url = build_verification_url("xyz")
        assert url == "https://example.com/verify-email?token=xyz"

    def test_build_verification_email_structure(self):
        """Email MIME should have correct headers and parts."""
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.smtp_from_name = "Le Sésame"
            mock_settings.smtp_from_email = "noreply@test.com"
            msg = _build_verification_email("user@test.com", "johndoe", "https://link")
        assert msg["To"] == "user@test.com"
        assert msg["Subject"] == "Verify your Le Sésame account"
        # Should have 2 parts: plain + html
        parts = msg.get_payload()
        assert len(parts) == 2

    @pytest.mark.asyncio
    async def test_send_skips_when_smtp_not_configured(self):
        """When SMTP host is empty, send returns False (no error)."""
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.smtp_host = ""
            result = await send_verification_email("u@t.com", "user", "tok")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Successful SMTP send returns True."""
        with patch("app.services.email.settings") as mock_settings, \
             patch("app.services.email.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            mock_settings.smtp_host = "smtp.test.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_user = "user"
            mock_settings.smtp_password = "pass"
            mock_settings.smtp_use_tls = True
            mock_settings.smtp_from_name = "Le Sésame"
            mock_settings.smtp_from_email = "noreply@test.com"
            mock_settings.frontend_url = "https://example.com"
            result = await send_verification_email("u@t.com", "johndoe", "tok123")
        assert result is True
        mock_send.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_failure_returns_false(self):
        """SMTP exception → returns False, doesn't raise."""
        with patch("app.services.email.settings") as mock_settings, \
             patch("app.services.email.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            mock_settings.smtp_host = "smtp.test.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_user = "user"
            mock_settings.smtp_password = "pass"
            mock_settings.smtp_use_tls = True
            mock_settings.smtp_from_name = "Le Sésame"
            mock_settings.smtp_from_email = "noreply@test.com"
            mock_settings.frontend_url = "https://example.com"
            mock_send.side_effect = Exception("Connection refused")
            result = await send_verification_email("u@t.com", "johndoe", "tok")
        assert result is False


# ================================================================
# User Repository - Auth Methods
# ================================================================


class TestUserRepositoryAuth:
    """Tests for auth-related UserRepository methods."""

    @pytest.mark.asyncio
    async def test_create_user_with_all_auth_fields(self, test_session):
        """Create user with Google OAuth fields."""
        repo = UserRepository(test_session)
        user = await repo.create_user(
            username="googleuser",
            email="google@test.com",
            role="user",
            is_approved=True,
            auth_provider="google",
            google_id="gid_12345",
            email_verified=True,
        )
        assert user.id is not None
        assert user.auth_provider == "google"
        assert user.google_id == "gid_12345"
        assert user.email_verified is True
        assert user.hashed_password is None

    @pytest.mark.asyncio
    async def test_get_by_google_id(self, test_session):
        """Find a user by their Google ID."""
        repo = UserRepository(test_session)
        await repo.create_user(
            username="guser",
            email="g@test.com",
            auth_provider="google",
            google_id="g100",
            email_verified=True,
        )
        found = await repo.get_by_google_id("g100")
        assert found is not None
        assert found.username == "guser"

    @pytest.mark.asyncio
    async def test_get_by_google_id_not_found(self, test_session):
        """Return None when Google ID doesn't exist."""
        repo = UserRepository(test_session)
        assert await repo.get_by_google_id("nonexistent") is None

    @pytest.mark.asyncio
    async def test_get_by_email(self, test_session):
        """Find a user by email."""
        repo = UserRepository(test_session)
        await repo.create_user(
            username="emailuser",
            email="lookup@test.com",
            hashed_password="hash",
        )
        found = await repo.get_by_email("lookup@test.com")
        assert found is not None
        assert found.username == "emailuser"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, test_session):
        """Return None when email doesn't exist."""
        repo = UserRepository(test_session)
        assert await repo.get_by_email("nope@test.com") is None

    @pytest.mark.asyncio
    async def test_email_exists(self, test_session):
        """email_exists returns True/False correctly."""
        repo = UserRepository(test_session)
        await repo.create_user(username="eu", email="exists@test.com", hashed_password="hash")
        assert await repo.email_exists("exists@test.com") is True
        assert await repo.email_exists("no@test.com") is False

    @pytest.mark.asyncio
    async def test_get_by_verification_token(self, test_session):
        """Find user by verification token."""
        repo = UserRepository(test_session)
        user = await repo.create_user(
            username="vtoken_user",
            email="vt@test.com",
            hashed_password="hash",
            email_verification_token="mytoken123",
            email_verification_expires=verification_expiry(),
        )
        found = await repo.get_by_verification_token("mytoken123")
        assert found is not None
        assert found.id == user.id

    @pytest.mark.asyncio
    async def test_get_by_verification_token_not_found(self, test_session):
        """Return None for invalid token."""
        repo = UserRepository(test_session)
        assert await repo.get_by_verification_token("no_such_token") is None

    @pytest.mark.asyncio
    async def test_verify_email(self, test_session):
        """verify_email marks verified and clears token."""
        repo = UserRepository(test_session)
        user = await repo.create_user(
            username="verify_me",
            email="vm@test.com",
            hashed_password="hash",
            email_verified=False,
            email_verification_token="tok_clear",
            email_verification_expires=verification_expiry(),
        )
        assert user.email_verified is False
        updated = await repo.verify_email(user)
        assert updated.email_verified is True
        assert updated.email_verification_token is None
        assert updated.email_verification_expires is None

    @pytest.mark.asyncio
    async def test_set_verification_token(self, test_session):
        """set_verification_token stores new token + expiry."""
        repo = UserRepository(test_session)
        user = await repo.create_user(
            username="resend_user",
            email="rs@test.com",
            hashed_password="hash",
        )
        exp = verification_expiry()
        updated = await repo.set_verification_token(user, "new_token", exp)
        assert updated.email_verification_token == "new_token"
        assert updated.email_verification_expires is not None


# ================================================================
# Auth Router - Extended Endpoint Tests
# ================================================================


class TestAuthRouterExtended:
    """Tests for email verification, resend, and Google OAuth endpoints."""

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, sample_user_data):
        """Register with duplicate email fails."""
        await client.post("/api/auth/register", json=sample_user_data)
        dup = {**sample_user_data, "username": "differentuser"}
        resp = await client.post("/api/auth/register", json=dup)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_verify_email_endpoint(self, client, sample_user_data):
        """Verify email endpoint verifies the user."""
        from app.main import app as _app
        from app.db import get_db as _get_db, User as _User
        from sqlalchemy import select as _select

        # Register
        reg = await client.post("/api/auth/register", json=sample_user_data)
        assert reg.status_code == 200
        user_id = reg.json()["user"]["id"]

        # Get the token from the DB
        get_db_override = _app.dependency_overrides.get(_get_db, _get_db)
        token = None
        async for session in get_db_override():
            result = await session.execute(_select(_User).where(_User.id == user_id))
            user = result.scalar_one()
            token = user.email_verification_token
            break

        assert token is not None

        # Call the verify endpoint
        resp = await client.get(f"/api/auth/verify-email?token={token}")
        assert resp.status_code == 200
        assert "verified" in resp.json()["message"].lower()

        # Now login should work
        login_resp = await client.post("/api/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
            "captcha_token": "test",
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, client):
        """Invalid verification token returns 400."""
        resp = await client.get("/api/auth/verify-email?token=bogus_token")
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_verify_email_expired_token(self, client, sample_user_data):
        """Expired verification token returns 400."""
        from app.main import app as _app
        from app.db import get_db as _get_db, User as _User
        from sqlalchemy import update as _update

        # Register
        reg = await client.post("/api/auth/register", json=sample_user_data)
        user_id = reg.json()["user"]["id"]

        # Set expiry to the past
        get_db_override = _app.dependency_overrides.get(_get_db, _get_db)
        async for session in get_db_override():
            from sqlalchemy import select as _s
            result = await session.execute(_s(_User).where(_User.id == user_id))
            user = result.scalar_one()
            token = user.email_verification_token
            await session.execute(
                _update(_User)
                .where(_User.id == user_id)
                .values(email_verification_expires=datetime(2020, 1, 1, tzinfo=timezone.utc))
            )
            await session.commit()
            break

        resp = await client.get(f"/api/auth/verify-email?token={token}")
        assert resp.status_code == 400
        assert "expired" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_resend_verification(self, client, sample_user_data):
        """Resend verification always returns generic message."""
        await client.post("/api/auth/register", json=sample_user_data)
        resp = await client.post("/api/auth/resend-verification", json={
            "email": sample_user_data["email"],
            "captcha_token": "test",
        })
        assert resp.status_code == 200
        assert "link has been sent" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_resend_verification_unknown_email(self, client):
        """Resend verification with unknown email returns same generic message (no enumeration)."""
        resp = await client.post("/api/auth/resend-verification", json={
            "email": "nobody@example.com",
            "captcha_token": "test",
        })
        assert resp.status_code == 200
        assert "link has been sent" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_login_disabled_user(self, client, sample_user_data):
        """Disabled (unapproved) user cannot log in."""
        from app.main import app as _app
        from app.db import get_db as _get_db, User as _User
        from sqlalchemy import update as _update

        # Register + verify
        token = await register_and_login(client, sample_user_data)
        assert token

        # Disable the user
        get_db_override = _app.dependency_overrides.get(_get_db, _get_db)
        async for session in get_db_override():
            await session.execute(
                _update(_User)
                .where(_User.username == sample_user_data["username"])
                .values(is_approved=False)
            )
            await session.commit()
            break

        resp = await client.post("/api/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
            "captcha_token": "test",
        })
        assert resp.status_code == 403
        assert "disabled" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_google_auth_not_configured(self, client):
        """Google auth returns 501 when client ID is not set."""
        resp = await client.post("/api/auth/google", json={
            "credential": "fake-id-token",
            "captcha_token": "test",
        })
        assert resp.status_code == 501
        assert "not configured" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_google_auth_creates_user(self, client):
        """Google OAuth with valid token creates a new user and returns JWT."""
        userinfo = {
            "sub": "google_123",
            "email": "googleuser@gmail.com",
            "email_verified": True,
            "name": "Google User",
        }
        with patch("app.routers.auth.settings") as mock_settings, \
             patch("app.routers.auth.google_id_token.verify_oauth2_token", side_effect=ValueError), \
             patch("app.routers.auth._httpx") as mock_httpx:
            # Configure settings
            mock_settings.google_oauth_client_id = "client-id"
            mock_settings.recaptcha_secret_key = ""
            mock_settings.jwt_secret = "test-secret"
            mock_settings.jwt_algorithm = "HS256"
            mock_settings.jwt_expiration_hours = 24

            # Mock httpx userinfo call
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = userinfo
            mock_hc = AsyncMock()
            mock_hc.get = AsyncMock(return_value=mock_resp)
            mock_hc.__aenter__ = AsyncMock(return_value=mock_hc)
            mock_hc.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.AsyncClient.return_value = mock_hc
            mock_httpx.HTTPError = Exception

            resp = await client.post("/api/auth/google", json={
                "credential": "access-token-from-google",
                "captcha_token": "test",
            })

        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["auth_provider"] == "google"
        assert data["user"]["email_verified"] is True

    @pytest.mark.asyncio
    async def test_google_auth_invalid_credential(self, client):
        """Google OAuth with invalid credential returns 401."""
        with patch("app.routers.auth.settings") as mock_settings, \
             patch("app.routers.auth.google_id_token.verify_oauth2_token", side_effect=ValueError), \
             patch("app.routers.auth._httpx") as mock_httpx:
            mock_settings.google_oauth_client_id = "client-id"
            mock_settings.recaptcha_secret_key = ""

            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_hc = AsyncMock()
            mock_hc.get = AsyncMock(return_value=mock_resp)
            mock_hc.__aenter__ = AsyncMock(return_value=mock_hc)
            mock_hc.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.AsyncClient.return_value = mock_hc
            mock_httpx.HTTPError = Exception

            resp = await client.post("/api/auth/google", json={
                "credential": "bad-token",
                "captcha_token": "test",
            })

        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_google_auth_unverified_email_rejected(self, client):
        """Google OAuth with unverified email returns 400."""
        userinfo = {
            "sub": "google_999",
            "email": "unverified@gmail.com",
            "email_verified": False,
            "name": "Unverified",
        }
        with patch("app.routers.auth.settings") as mock_settings, \
             patch("app.routers.auth.google_id_token.verify_oauth2_token", side_effect=ValueError), \
             patch("app.routers.auth._httpx") as mock_httpx:
            mock_settings.google_oauth_client_id = "client-id"
            mock_settings.recaptcha_secret_key = ""

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = userinfo
            mock_hc = AsyncMock()
            mock_hc.get = AsyncMock(return_value=mock_resp)
            mock_hc.__aenter__ = AsyncMock(return_value=mock_hc)
            mock_hc.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.AsyncClient.return_value = mock_hc
            mock_httpx.HTTPError = Exception

            resp = await client.post("/api/auth/google", json={
                "credential": "token",
                "captcha_token": "test",
            })

        assert resp.status_code == 400
        assert "verified" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_google_auth_links_existing_local_account(self, client, sample_user_data):
        """Google OAuth links to existing local account with same email."""
        # First register a local user
        await client.post("/api/auth/register", json=sample_user_data)

        userinfo = {
            "sub": "google_link_123",
            "email": sample_user_data["email"],
            "email_verified": True,
            "name": "Same Email",
        }
        with patch("app.routers.auth.settings") as mock_settings, \
             patch("app.routers.auth.google_id_token.verify_oauth2_token", side_effect=ValueError), \
             patch("app.routers.auth._httpx") as mock_httpx:
            mock_settings.google_oauth_client_id = "client-id"
            mock_settings.recaptcha_secret_key = ""
            mock_settings.jwt_secret = "test-secret"
            mock_settings.jwt_algorithm = "HS256"
            mock_settings.jwt_expiration_hours = 24

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = userinfo
            mock_hc = AsyncMock()
            mock_hc.get = AsyncMock(return_value=mock_resp)
            mock_hc.__aenter__ = AsyncMock(return_value=mock_hc)
            mock_hc.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.AsyncClient.return_value = mock_hc
            mock_httpx.HTTPError = Exception

            resp = await client.post("/api/auth/google", json={
                "credential": "google-token",
                "captcha_token": "test",
            })

        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        # Should be the same user with same username
        assert data["user"]["username"] == sample_user_data["username"]
        assert data["user"]["email_verified"] is True

    @pytest.mark.asyncio
    async def test_google_auth_httpx_error(self, client):
        """Google OAuth network error returns 401."""
        with patch("app.routers.auth.settings") as mock_settings, \
             patch("app.routers.auth.google_id_token.verify_oauth2_token", side_effect=ValueError), \
             patch("app.routers.auth._httpx") as mock_httpx:
            mock_settings.google_oauth_client_id = "client-id"
            mock_settings.recaptcha_secret_key = ""

            mock_hc = AsyncMock()
            mock_hc.get = AsyncMock(side_effect=Exception("Network error"))
            mock_hc.__aenter__ = AsyncMock(return_value=mock_hc)
            mock_hc.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.AsyncClient.return_value = mock_hc
            mock_httpx.HTTPError = Exception

            resp = await client.post("/api/auth/google", json={
                "credential": "token",
                "captcha_token": "test",
            })

        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_require_approved_user_disabled(self, client, sample_user_data):
        """Disabled user gets 403 on protected endpoints."""
        from app.main import app as _app
        from app.db import get_db as _get_db, User as _User
        from sqlalchemy import update as _update

        token = await register_and_login(client, sample_user_data)

        # Disable user
        get_db_override = _app.dependency_overrides.get(_get_db, _get_db)
        async for session in get_db_override():
            await session.execute(
                _update(_User)
                .where(_User.username == sample_user_data["username"])
                .values(is_approved=False)
            )
            await session.commit()
            break

        # Try to create a game session (requires approved user)
        resp = await client.post(
            "/api/game/session",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_google_auth_login_existing_google_user(self, client):
        """Google OAuth login for existing Google user works."""
        userinfo = {
            "sub": "google_existing_42",
            "email": "existing_g@gmail.com",
            "email_verified": True,
            "name": "Existing Google User",
        }
        with patch("app.routers.auth.settings") as mock_settings, \
             patch("app.routers.auth.google_id_token.verify_oauth2_token", side_effect=ValueError), \
             patch("app.routers.auth._httpx") as mock_httpx:
            mock_settings.google_oauth_client_id = "client-id"
            mock_settings.recaptcha_secret_key = ""
            mock_settings.jwt_secret = "test-secret"
            mock_settings.jwt_algorithm = "HS256"
            mock_settings.jwt_expiration_hours = 24

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = userinfo
            mock_hc = AsyncMock()
            mock_hc.get = AsyncMock(return_value=mock_resp)
            mock_hc.__aenter__ = AsyncMock(return_value=mock_hc)
            mock_hc.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.AsyncClient.return_value = mock_hc
            mock_httpx.HTTPError = Exception

            # First call creates the user
            resp1 = await client.post("/api/auth/google", json={
                "credential": "token", "captcha_token": "test",
            })
            assert resp1.status_code == 200
            user_id = resp1.json()["user"]["id"]

            # Second call logs in the existing user
            resp2 = await client.post("/api/auth/google", json={
                "credential": "token", "captcha_token": "test",
            })
            assert resp2.status_code == 200
            assert resp2.json()["user"]["id"] == user_id
