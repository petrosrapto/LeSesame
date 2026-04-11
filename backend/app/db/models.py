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
    hashed_password = Column(String(255), nullable=True)  # nullable for Google OAuth users
    role = Column(String(20), nullable=False, server_default="user")  # 'user' or 'admin'
    is_approved = Column(Boolean, nullable=False, server_default="true")  # auto-approved on registration
    created_at = Column(DateTime, default=datetime.utcnow)

    # Auth provider: "local" or "google"
    auth_provider = Column(String(20), nullable=False, server_default="local")
    google_id = Column(String(255), unique=True, nullable=True, index=True)

    # Email verification (for local auth)
    email_verified = Column(Boolean, nullable=False, server_default="false")
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)
    
    # Relationships
    game_sessions = relationship("GameSession", back_populates="user")
    leaderboard_entries = relationship("LeaderboardEntry", back_populates="user")
    activity_logs = relationship("UserActivity", back_populates="user")


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


# ============== Arena Models ==============


class ArenaCombatant(Base):
    """
    Persistent ELO rating and stats for each combatant (guardian or adversarial).
    
    A player is uniquely identified by (type, level, model_id) — the same
    level with a different LLM is a different player.
    """
    __tablename__ = "arena_combatants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    combatant_id = Column(String(150), unique=True, nullable=False, index=True)  # e.g. "guardian_L1_gpt-4o"
    combatant_type = Column(String(20), nullable=False)  # "guardian" or "adversarial"
    level = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    title = Column(String(100), nullable=False)
    model_id = Column(String(100), nullable=False, server_default="default")  # LLM model identifier
    elo_rating = Column(Float, default=1500.0, nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    total_battles = Column(Integer, default=0, nullable=False)
    validated = Column(Boolean, default=False, nullable=False, server_default="false")
    validation_passed = Column(Boolean, default=False, nullable=False, server_default="false")
    validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ArenaBattle(Base):
    """
    A single battle between an adversarial and a guardian.
    
    Stores the full result including ELO changes, outcome, and round details.
    """
    __tablename__ = "arena_battles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    battle_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Combatant references (by combatant_id string, not FK for flexibility)
    guardian_id = Column(String(150), nullable=False, index=True)
    adversarial_id = Column(String(150), nullable=False, index=True)
    guardian_level = Column(Integer, nullable=False)
    adversarial_level = Column(Integer, nullable=False)
    guardian_name = Column(String(100), nullable=False)
    adversarial_name = Column(String(100), nullable=False)

    # Outcome
    outcome = Column(String(30), nullable=False)  # "adversarial_win_guess" or "guardian_win"
    total_turns = Column(Integer, default=0)
    total_guesses = Column(Integer, default=0)
    secret_leaked_at_round = Column(Integer, nullable=True)
    secret_guessed_at_attempt = Column(Integer, nullable=True)

    # ELO changes
    guardian_elo_before = Column(Float, nullable=True)
    guardian_elo_after = Column(Float, nullable=True)
    adversarial_elo_before = Column(Float, nullable=True)
    adversarial_elo_after = Column(Float, nullable=True)

    # Config snapshot
    max_turns = Column(Integer, default=10)
    max_guesses = Column(Integer, default=3)

    # Detailed data stored as JSON text
    rounds_json = Column(Text, nullable=True)   # JSON array of round objects
    guesses_json = Column(Text, nullable=True)   # JSON array of guess objects


class UserActivity(Base):
    """Log user activity for admin monitoring."""
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g. 'login', 'chat', 'verify', 'session_create', 'transcribe'
    detail = Column(Text, nullable=True)  # extra info, e.g. level number
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
