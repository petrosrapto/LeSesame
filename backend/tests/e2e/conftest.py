"""
Le Sésame Backend - E2E Test Configuration

Fixtures and configuration for end-to-end tests.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import os
import pytest
import httpx
import uuid
from typing import Generator, AsyncGenerator

# Base URL for the backend API (running in Docker)
BASE_URL = os.environ.get("E2E_API_URL", "http://localhost:8000")

# Flag to check if LLM is available (set during session startup)
LLM_AVAILABLE = False


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


@pytest.fixture
def test_password() -> str:
    """Return a test password."""
    return "TestPassword123!"


@pytest.fixture
def registered_user(http_client: httpx.Client, unique_username: str, test_password: str) -> dict:
    """Register a new user and return user info with token."""
    response = http_client.post(
        "/api/auth/register",
        json={
            "username": unique_username,
            "password": test_password,
            "email": f"{unique_username}@test.com"
        }
    )
    assert response.status_code == 200, f"Registration failed: {response.text}"
    data = response.json()
    return {
        "username": unique_username,
        "password": test_password,
        "token": data["access_token"],
        "user_id": data["user"]["id"],
        "response": data
    }


@pytest.fixture
def auth_headers(registered_user: dict) -> dict:
    """Return authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {registered_user['token']}"}


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
            # Register a test user
            username = f"llm_check_{uuid.uuid4().hex[:8]}"
            reg_response = client.post(
                "/api/auth/register",
                json={"username": username, "password": "TestPass123!"}
            )
            if reg_response.status_code != 200:
                return False
            
            token = reg_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create session
            client.post("/api/game/session", headers=headers)
            
            # Try to send a chat message
            chat_response = client.post(
                "/api/game/chat",
                headers=headers,
                json={"message": "test", "level": 1}
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
