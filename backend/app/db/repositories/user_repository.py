"""
Le Sésame Backend - User Repository

Repository for User-related database operations.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload

from .base import BaseRepository
from ..models import User, GameSession, LevelAttempt, ChatMessage, LeaderboardEntry, UserActivity


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

    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get a user by Google ID."""
        result = await self._session.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()
    
    async def username_exists(self, username: str) -> bool:
        """Check if a username already exists."""
        user = await self.get_by_username(username)
        return user is not None
    
    async def email_exists(self, email: str) -> bool:
        """Check if an email already exists."""
        user = await self.get_by_email(email)
        return user is not None
    
    async def create_user(
        self,
        username: str,
        hashed_password: Optional[str] = None,
        email: Optional[str] = None,
        role: str = "user",
        is_approved: bool = True,
        auth_provider: str = "local",
        google_id: Optional[str] = None,
        email_verified: bool = False,
        email_verification_token: Optional[str] = None,
        email_verification_expires: Optional[datetime] = None,
    ) -> User:
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_approved=is_approved,
            auth_provider=auth_provider,
            google_id=google_id,
            email_verified=email_verified,
            email_verification_token=email_verification_token,
            email_verification_expires=email_verification_expires,
        )
        return await self.create(user)
    
    async def approve_user(self, user: User) -> User:
        """Approve a user (admin action)."""
        user.is_approved = True
        return await self.update(user)
    
    async def disapprove_user(self, user: User) -> User:
        """Revoke approval from a user (admin action)."""
        user.is_approved = False
        return await self.update(user)
    
    async def set_role(self, user: User, role: str) -> User:
        """Set a user's role."""
        user.role = role
        return await self.update(user)

    async def get_by_verification_token(self, token: str) -> Optional[User]:
        """Get a user by their email verification token."""
        result = await self._session.execute(
            select(User).where(User.email_verification_token == token)
        )
        return result.scalar_one_or_none()

    async def verify_email(self, user: User) -> User:
        """Mark user email as verified and clear the token."""
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        return await self.update(user)

    async def set_verification_token(
        self, user: User, token: str, expires: datetime,
    ) -> User:
        """Set a new verification token on a user."""
        user.email_verification_token = token
        user.email_verification_expires = expires
        return await self.update(user)
    
    async def get_all_users(self, page: int = 1, per_page: int = 50) -> tuple[List[User], int]:
        """Get all users with pagination and total count."""
        count_result = await self._session.execute(
            select(func.count(User.id))
        )
        total = count_result.scalar_one()
        
        offset = (page - 1) * per_page
        result = await self._session.execute(
            select(User).order_by(User.created_at.desc()).limit(per_page).offset(offset)
        )
        users = list(result.scalars().all())
        return users, total
    
    async def delete_user_cascade(self, user: User) -> None:
        """Delete a user and all related data (sessions, attempts, messages, leaderboard, activity)."""
        # Delete activity logs
        await self._session.execute(
            delete(UserActivity).where(UserActivity.user_id == user.id)
        )
        
        # Get all session IDs for this user
        session_result = await self._session.execute(
            select(GameSession.id).where(GameSession.user_id == user.id)
        )
        session_ids = [row[0] for row in session_result.all()]
        
        if session_ids:
            await self._session.execute(
                delete(ChatMessage).where(ChatMessage.session_id.in_(session_ids))
            )
            await self._session.execute(
                delete(LevelAttempt).where(LevelAttempt.session_id.in_(session_ids))
            )
            await self._session.execute(
                delete(GameSession).where(GameSession.user_id == user.id)
            )
        
        await self._session.execute(
            delete(LeaderboardEntry).where(LeaderboardEntry.user_id == user.id)
        )
        
        await self.delete(user)
    
    async def get_activity_logs(
        self, user_id: Optional[int] = None, page: int = 1, per_page: int = 50,
    ) -> tuple[List[UserActivity], int]:
        """Get activity logs, optionally filtered by user_id."""
        base_query = select(UserActivity).options(joinedload(UserActivity.user))
        count_query = select(func.count(UserActivity.id))
        
        if user_id:
            base_query = base_query.where(UserActivity.user_id == user_id)
            count_query = count_query.where(UserActivity.user_id == user_id)
        
        count_result = await self._session.execute(count_query)
        total = count_result.scalar_one()
        
        offset = (page - 1) * per_page
        result = await self._session.execute(
            base_query.order_by(UserActivity.timestamp.desc()).limit(per_page).offset(offset)
        )
        logs = list(result.scalars().all())
        return logs, total
