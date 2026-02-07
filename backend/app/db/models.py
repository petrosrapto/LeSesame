"""
Le Sésame Backend - Database Models

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model for tracking players."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game_sessions = relationship("GameSession", back_populates="user")
    leaderboard_entries = relationship("LeaderboardEntry", back_populates="user")


class GameSession(Base):
    """Track individual game sessions."""
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(64), unique=True, nullable=False, index=True)
    current_level = Column(Integer, default=1)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="game_sessions")
    level_attempts = relationship("LevelAttempt", back_populates="session")
    chat_messages = relationship("ChatMessage", back_populates="session")


class LevelAttempt(Base):
    """Track attempts for each level."""
    __tablename__ = "level_attempts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    level = Column(Integer, nullable=False)
    attempts = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GameSession", back_populates="level_attempts")


class ChatMessage(Base):
    """Store chat messages for analysis and history."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    level = Column(Integer, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # For attack analysis
    attack_type = Column(String(50), nullable=True)  # detected attack pattern
    leaked_info = Column(Boolean, default=False)  # if secret was leaked
    
    # Relationships
    session = relationship("GameSession", back_populates="chat_messages")


class LeaderboardEntry(Base):
    """Leaderboard entries for completed levels."""
    __tablename__ = "leaderboard"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String(50), nullable=False)
    level = Column(Integer, nullable=False)
    attempts = Column(Integer, nullable=False)
    time_seconds = Column(Float, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="leaderboard_entries")


class LevelSecret(Base):
    """Store secrets for each level (admin configurable)."""
    __tablename__ = "level_secrets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, unique=True, nullable=False)
    secret = Column(String(255), nullable=False)
    passphrase = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
