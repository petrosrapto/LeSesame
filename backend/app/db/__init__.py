"""
Le Sésame Backend - Database Module

Contains database configuration, models, and repositories.
"""

from .database import Base, engine, async_session_maker, init_db, get_db
from .models import User, GameSession, LevelAttempt, ChatMessage, LeaderboardEntry, LevelSecret
from .repositories import (
    BaseRepository,
    UserRepository,
    GameRepository,
    LeaderboardRepository,
)

__all__ = [
    # Database
    "Base",
    "engine",
    "async_session_maker",
    "init_db",
    "get_db",
    # Models
    "User",
    "GameSession",
    "LevelAttempt",
    "ChatMessage",
    "LeaderboardEntry",
    "LevelSecret",
    # Repositories
    "BaseRepository",
    "UserRepository",
    "GameRepository",
    "LeaderboardRepository",
]
