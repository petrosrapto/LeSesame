"""
Le Sésame Backend - User Repository

Repository for User-related database operations.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseRepository
from ..models import User


class UserRepository(BaseRepository[User]):
    """Repository for User entity operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self._session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def username_exists(self, username: str) -> bool:
        """Check if a username already exists."""
        user = await self.get_by_username(username)
        return user is not None
    
    async def create_user(
        self,
        username: str,
        hashed_password: str,
        email: Optional[str] = None
    ) -> User:
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        return await self.create(user)
