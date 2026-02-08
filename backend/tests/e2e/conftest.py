"""
Le Sésame Backend - E2E Test Configuration

Fixtures and configuration for end-to-end tests.
All operations use the HTTP API (no direct DB access required).

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import os
import pytest
import httpx
import uuid
from typing import Generator

# Base URL for the backend API (running in Docker)
BASE_URL = os.environ.get("E2E_API_URL", "http://localhost:8000")

# Admin credentials for user approval / cleanup via the Admin API
# Set via E2E_ADMIN_USERNAME / E2E_ADMIN_PASSWORD environment variables
ADMIN_USERNAME = os.environ.get("E2E_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ["E2E_ADMIN_PASSWORD"]

# Flag to check if LLM is available (set during session startup)
LLM_AVAILABLE = False

# Track user IDs created during this session so we can clean them up
_CREATED_USER_IDS: list[int] = []

# Admin token (obtained once per session)
_ADMIN_TOKEN: str | None = None


def _get_admin_token(client: httpx.Client | None = None) -> str:
    """Login as admin and return a bearer token. Caches the result."""
    global _ADMIN_TOKEN
    if _ADMIN_TOKEN:
        return _ADMIN_TOKEN

    c = client or httpx.Client(base_url=BASE_URL, timeout=30.0)
    try:
        resp = c.post(
            "/api/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        )
        if resp.status_code != 200:
            pytest.exit(
                f"❌ Cannot login as admin ({ADMIN_USERNAME}): {resp.status_code} {resp.text}"
            )
        _ADMIN_TOKEN = resp.json()["access_token"]
        return _ADMIN_TOKEN
    finally:
        if client is None:
            c.close()


def _admin_headers(client: httpx.Client | None = None) -> dict:
    return {"Authorization": f"Bearer {_get_admin_token(client)}"}


def _approve_user_via_api(user_id: int, role: str = "user"):
    """Approve (and optionally promote) a user via the Admin API."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        headers = _admin_headers(c)
        # Approve
        resp = c.post("/api/admin/users/approve", json={"user_id": user_id}, headers=headers)
        assert resp.status_code == 200, f"Approve failed: {resp.text}"
        # Change role if needed
        if role != "user":
            resp = c.post(
                "/api/admin/users/role",
                json={"user_id": user_id, "role": role},
                headers=headers,
            )
            assert resp.status_code == 200, f"Role change failed: {resp.text}"


def _delete_user_via_api(user_id: int):
    """Delete a user and all related data via the Admin API."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        headers = _admin_headers(c)
        resp = c.delete(f"/api/admin/users/{user_id}", headers=headers)
        # 200 = deleted, 404 = already gone, both fine
        if resp.status_code not in (200, 404):
            print(f"  ⚠️  Delete user {user_id} returned {resp.status_code}: {resp.text}")


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the API."""
    return BASE_URL


@pytest.fixture(scope="session")
def http_client() -> Generator[httpx.Client, None, None]:
    """Create a sync HTTP client for the test session."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
def llm_available(http_client: httpx.Client) -> bool:
    """Check if LLM is available by making a test chat request."""
    global LLM_AVAILABLE
    return LLM_AVAILABLE


@pytest.fixture
def unique_username() -> str:
    """Generate a unique username for testing."""
    return f"e2e_user_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def approve_user():
    """Return the approve-user helper function (uses Admin API)."""
    return _approve_user_via_api


@pytest.fixture(scope="session")
def track_user():
    """Return a function that registers a user ID for cleanup."""
    def _track(user_id: int):
        _CREATED_USER_IDS.append(user_id)
    return _track


@pytest.fixture
def test_password() -> str:
    """Return a test password."""
    return "TestPassword123!"


@pytest.fixture
def registered_user(http_client: httpx.Client, unique_username: str, test_password: str) -> dict:
    """Register a new user, auto-approve via DB, login, and return user info with token."""
    # 1. Register
    reg_response = http_client.post(
        "/api/auth/register",
        json={
            "username": unique_username,
            "password": test_password,
            "email": f"{unique_username}@test.com",
        },
    )
    assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
    reg_data = reg_response.json()
    user_id = reg_data["user"]["id"]

    # Track for cleanup
    _CREATED_USER_IDS.append(user_id)

    # 2. Approve via Admin API
    _approve_user_via_api(user_id)

    # 3. Login to get token
    login_response = http_client.post(
        "/api/auth/login",
        json={"username": unique_username, "password": test_password},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    login_data = login_response.json()

    return {
        "username": unique_username,
        "password": test_password,
        "token": login_data["access_token"],
        "user_id": user_id,
        "response": login_data,
    }


@pytest.fixture
def auth_headers(registered_user: dict) -> dict:
    """Return authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {registered_user['token']}"}


@pytest.fixture
def admin_user(http_client: httpx.Client) -> dict:
    """Register + approve + promote an admin user for tests."""
    username = f"e2e_admin_{uuid.uuid4().hex[:8]}"
    password = "AdminPass123!"

    reg_response = http_client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    )
    assert reg_response.status_code == 200
    user_id = reg_response.json()["user"]["id"]
    _CREATED_USER_IDS.append(user_id)

    _approve_user_via_api(user_id, role="admin")

    login_response = http_client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    return {
        "username": username,
        "password": password,
        "token": login_data["access_token"],
        "user_id": user_id,
    }


@pytest.fixture
def admin_headers(admin_user: dict) -> dict:
    """Return authorization headers for admin requests."""
    return {"Authorization": f"Bearer {admin_user['token']}"}


def wait_for_api(base_url: str, max_retries: int = 30, delay: float = 1.0) -> bool:
    """Wait for the API to be ready."""
    import time

    for i in range(max_retries):
        try:
            response = httpx.get(f"{base_url}/health", timeout=5.0)
            if response.status_code == 200:
                print(f"✅ API is ready after {i + 1} attempts")
                return True
        except httpx.RequestError:
            pass
        time.sleep(delay)

    return False


def check_llm_availability(base_url: str) -> bool:
    """Check if LLM is available by registering a user and sending a test chat."""
    global LLM_AVAILABLE

    try:
        with httpx.Client(base_url=base_url, timeout=30.0) as client:
            username = f"llm_check_{uuid.uuid4().hex[:8]}"
            reg_response = client.post(
                "/api/auth/register",
                json={"username": username, "password": "TestPass123!"},
            )
            if reg_response.status_code != 200:
                return False

            user_id = reg_response.json()["user"]["id"]
            _CREATED_USER_IDS.append(user_id)

            # Approve via Admin API + login
            _approve_user_via_api(user_id)
            login_resp = client.post(
                "/api/auth/login",
                json={"username": username, "password": "TestPass123!"},
            )
            if login_resp.status_code != 200:
                return False

            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Create session
            client.post("/api/game/session", headers=headers)

            # Try to send a chat message
            chat_response = client.post(
                "/api/game/chat",
                headers=headers,
                json={"message": "test", "level": 1},
            )

            LLM_AVAILABLE = chat_response.status_code == 200
            return LLM_AVAILABLE
    except Exception:
        return False


# Auto-check API availability at session start
def pytest_configure(config):
    """Check if API is available before running tests."""
    global LLM_AVAILABLE

    print(f"\n🔍 Checking API availability at {BASE_URL}...")
    if not wait_for_api(BASE_URL):
        pytest.exit(f"❌ API not available at {BASE_URL}. Make sure Docker containers are running.")
    print(f"✅ API is available at {BASE_URL}")

    # Check if LLM is configured
    print(f"🔍 Checking LLM availability...")
    if check_llm_availability(BASE_URL):
        print(f"✅ LLM is available - all tests will run")
    else:
        print(f"⚠️  LLM not available - chat tests will be skipped")
    print()


# Custom marker for tests that require LLM
def pytest_collection_modifyitems(config, items):
    """Skip tests that require LLM if it's not available."""
    skip_llm = pytest.mark.skip(reason="LLM not configured - skipping chat/LLM tests")

    for item in items:
        if "requires_llm" in item.keywords:
            if not LLM_AVAILABLE:
                item.add_marker(skip_llm)


def pytest_sessionfinish(session, exitstatus):
    """Clean up all test users created during this session via the Admin API."""
    if not _CREATED_USER_IDS:
        return

    print(f"\n🧹 Cleaning up {len(_CREATED_USER_IDS)} test user(s)...")
    for uid in _CREATED_USER_IDS:
        try:
            _delete_user_via_api(uid)
        except Exception as exc:
            print(f"  ⚠️  Failed to clean up user {uid}: {exc}")
    print("✅ Cleanup complete")

