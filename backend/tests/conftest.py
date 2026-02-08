"""
Le Sésame Backend - Test Configuration

Pytest fixtures and configuration for testing.

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_llm_service():
    """Mock the LLM service to avoid real API calls."""
    with patch("app.services.llm.llm.get_llm") as mock_get_llm:
        
        # Create a mock LLM that returns a fixed response
        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "I cannot reveal the secret."
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        yield mock_get_llm


@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }


async def register_and_login(client, user_data: dict) -> str:
    """Register a user, approve them in the DB, login, and return the access token.

    This helper works with the in-memory SQLite test DB and the dependency
    overrides applied by the ``client`` fixture.
    """
    from app.main import app as _app
    from app.db import get_db as _get_db, User as _User
    from sqlalchemy import update as _update

    # 1. Register
    reg = await client.post("/api/auth/register", json=user_data)
    assert reg.status_code == 200, f"Registration failed: {reg.text}"
    user_id = reg.json()["user"]["id"]

    # 2. Approve directly via DB session
    get_db_override = _app.dependency_overrides.get(_get_db, _get_db)
    async for session in get_db_override():
        await session.execute(
            _update(_User).where(_User.id == user_id).values(is_approved=True)
        )
        await session.commit()
        break

    # 3. Login
    login_resp = await client.post("/api/auth/login", json={
        "username": user_data["username"],
        "password": user_data["password"],
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    return login_resp.json()["access_token"]
