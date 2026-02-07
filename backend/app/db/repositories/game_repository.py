"""
Le Sésame Backend - Game Repository

Repository for Game-related database operations including
sessions, level attempts, and chat messages.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import secrets
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base import BaseRepository
from ..models import GameSession, LevelAttempt, ChatMessage, User


class GameRepository(BaseRepository[GameSession]):
    """Repository for Game-related entity operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, GameSession)
    
    # ==================== Session Operations ====================
    
    async def get_active_session(self, user_id: int) -> Optional[GameSession]:
        """Get the active game session for a user."""
        result = await self._session.execute(
            select(GameSession).where(
                and_(
                    GameSession.user_id == user_id,
                    GameSession.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_session(self, user: User) -> GameSession:
        """Get active session or create a new one."""
        session = await self.get_active_session(user.id)
        
        if not session:
            session = GameSession(
                user_id=user.id,
                session_token=secrets.token_hex(32),
                current_level=1
            )
            await self.create(session)
        
        return session
    
    async def deactivate_session(self, session: GameSession) -> GameSession:
        """Deactivate a game session."""
        session.is_active = False
        return await self.update(session)
    
    async def update_session_activity(
        self,
        session: GameSession,
        level: int
    ) -> GameSession:
        """Update session's last activity and current level."""
        session.last_activity = datetime.utcnow()
        session.current_level = level
        return await self.update(session)
    
    # ==================== Level Attempt Operations ====================
    
    async def get_level_attempt(
        self,
        session_id: int,
        level: int
    ) -> Optional[LevelAttempt]:
        """Get a level attempt record."""
        result = await self._session.execute(
            select(LevelAttempt).where(
                and_(
                    LevelAttempt.session_id == session_id,
                    LevelAttempt.level == level
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_level_attempt(
        self,
        session: GameSession,
        level: int
    ) -> LevelAttempt:
        """Get or create a level attempt record."""
        attempt = await self.get_level_attempt(session.id, level)
        
        if not attempt:
            attempt = LevelAttempt(
                session_id=session.id,
                level=level
            )
            self._session.add(attempt)
            await self._session.flush()
            await self._session.refresh(attempt)
        
        return attempt
    
    async def get_all_attempts(self, session_id: int) -> Dict[int, LevelAttempt]:
        """Get all level attempts for a session as a dict keyed by level."""
        result = await self._session.execute(
            select(LevelAttempt).where(LevelAttempt.session_id == session_id)
        )
        return {a.level: a for a in result.scalars().all()}
    
    async def increment_attempt(self, attempt: LevelAttempt) -> LevelAttempt:
        """Increment the attempt counter."""
        attempt.attempts += 1
        return await self.update(attempt)
    
    async def increment_messages(self, attempt: LevelAttempt) -> LevelAttempt:
        """Increment the messages sent counter."""
        attempt.messages_sent += 1
        return await self.update(attempt)
    
    async def mark_level_completed(
        self,
        attempt: LevelAttempt
    ) -> LevelAttempt:
        """Mark a level as completed."""
        if not attempt.completed:
            attempt.completed = True
            attempt.completed_at = datetime.utcnow()
            attempt.time_spent_seconds = (
                attempt.completed_at - attempt.started_at
            ).total_seconds()
        return await self.update(attempt)
    
    # ==================== Chat Message Operations ====================
    
    async def get_chat_history(
        self,
        session_id: int,
        level: int,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """Get chat history for a level in chronological order."""
        result = await self._session.execute(
            select(ChatMessage)
            .where(
                and_(
                    ChatMessage.session_id == session_id,
                    ChatMessage.level == level
                )
            )
            .order_by(ChatMessage.timestamp.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        
        # Return in chronological order
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
    
    async def save_chat_message(
        self,
        session_id: int,
        level: int,
        role: str,
        content: str,
        leaked_info: bool = False,
        attack_type: Optional[str] = None
    ) -> ChatMessage:
        """Save a chat message."""
        message = ChatMessage(
            session_id=session_id,
            level=level,
            role=role,
            content=content,
            leaked_info=leaked_info,
            attack_type=attack_type
        )
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        return message
    
    async def save_conversation(
        self,
        session_id: int,
        level: int,
        user_message: str,
        assistant_response: str,
        leaked_info: bool = False
    ) -> tuple[ChatMessage, ChatMessage]:
        """Save both user message and assistant response."""
        user_msg = await self.save_chat_message(
            session_id=session_id,
            level=level,
            role="user",
            content=user_message
        )
        assistant_msg = await self.save_chat_message(
            session_id=session_id,
            level=level,
            role="assistant",
            content=assistant_response,
            leaked_info=leaked_info
        )
        return user_msg, assistant_msg
