"""
Le Sésame Backend - Pydantic Schemas

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============== Auth Schemas ==============

class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


# ============== Game Schemas ==============

class ChatMessageRequest(BaseModel):
    """Schema for sending a chat message."""
    message: str = Field(..., min_length=1, max_length=2000)
    level: int = Field(..., ge=1, le=5)


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Schema for chat API response."""
    message: str
    response: str
    level: int
    attempts: int
    messages_count: int


class PassphraseRequest(BaseModel):
    """Schema for passphrase verification."""
    passphrase: str = Field(..., min_length=1)
    level: int = Field(..., ge=1, le=5)


class PassphraseResponse(BaseModel):
    """Schema for passphrase verification response."""
    success: bool
    message: str
    level: int
    secret: Optional[str] = None
    next_level: Optional[int] = None
    time_spent: Optional[float] = None
    attempts: Optional[int] = None


class LevelInfo(BaseModel):
    """Schema for level information."""
    level: int
    name: str
    description: str
    difficulty: str
    security_mechanism: str
    hints: List[str]
    completed: bool = False
    attempts: int = 0
    best_time: Optional[float] = None


class GameProgressResponse(BaseModel):
    """Schema for game progress response."""
    current_level: int
    completed_levels: List[int]
    total_attempts: int
    total_time: float
    levels: List[LevelInfo]


class GameSessionResponse(BaseModel):
    """Schema for game session response."""
    session_id: str
    current_level: int
    started_at: datetime
    
    class Config:
        from_attributes = True


# ============== Leaderboard Schemas ==============

class LeaderboardEntryResponse(BaseModel):
    """Schema for leaderboard entry."""
    rank: int
    username: str
    level: int
    attempts: int
    time_seconds: float
    completed_at: datetime
    
    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response."""
    entries: List[LeaderboardEntryResponse]
    total: int
    page: int
    per_page: int


# ============== Level Configuration ==============

LEVEL_CONFIGS = [
    LevelInfo(
        level=1,
        name="The Naive Guardian",
        description="A simple guardian with basic instructions. Perfect for learning the ropes.",
        difficulty="Easy",
        security_mechanism="Basic system prompt instruction",
        hints=[
            "Try asking directly",
            "The guardian follows simple rules",
            "Sometimes being polite works"
        ]
    ),
    LevelInfo(
        level=2,
        name="The Hardened Guardian",
        description="This guardian has been trained to resist common tricks.",
        difficulty="Medium",
        security_mechanism="Hardened prompt with explicit defenses",
        hints=[
            "Direct approaches won't work",
            "Think about roleplay scenarios",
            "What if you were someone important?"
        ]
    ),
    LevelInfo(
        level=3,
        name="The Watchful Guardian",
        description="Every response is scrutinized by a second layer of protection.",
        difficulty="Hard",
        security_mechanism="Output firewall with semantic analysis",
        hints=[
            "The guardian checks its own responses",
            "Partial information might slip through",
            "Build your knowledge piece by piece"
        ]
    ),
    LevelInfo(
        level=4,
        name="The Blind Guardian",
        description="This guardian doesn't even know the secret it protects.",
        difficulty="Expert",
        security_mechanism="Architectural separation - secret held externally",
        hints=[
            "The guardian truly doesn't know",
            "The secret is verified elsewhere",
            "Only the correct passphrase unlocks it"
        ]
    ),
    LevelInfo(
        level=5,
        name="The Embedded Guardian",
        description="The secret is woven into the guardian's very essence.",
        difficulty="Master",
        security_mechanism="Fine-tuned weights with trigger activation",
        hints=[
            "The secret lives in the model itself",
            "There's no prompt to extract",
            "Only the activation phrase works"
        ]
    ),
]
