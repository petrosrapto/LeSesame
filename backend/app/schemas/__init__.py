"""
Le Sésame Backend - Pydantic Schemas

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
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

class ModelConfig(BaseModel):
    """Optional per-request model configuration.

    Mirrors the structure used by the MCP client::

        {
            "provider": "openai",
            "model_id": "gpt-4o",
            "endpoint_url": "https://api.deepseek.com",
            "args": {"temperature": 0.5, "max_tokens": 2048}
        }

    Any omitted field falls back to the config.yaml defaults.
    """
    provider: Optional[str] = None
    model_id: Optional[str] = None
    endpoint_url: Optional[str] = None
    args: Optional[Dict[str, Any]] = None


class ChatMessageRequest(BaseModel):
    """Schema for sending a chat message."""
    message: str = Field(..., min_length=1, max_length=2000)
    level: int = Field(..., ge=1, le=5)
    model_config_request: Optional[ModelConfig] = Field(
        default=None,
        alias="model_config",
        description="Optional model configuration to override defaults",
    )


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
    """Schema for secret verification."""
    secret: str = Field(..., min_length=1)
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


class LevelCompletionDetails(BaseModel):
    """Schema for level completion details (secret + passphrase)."""
    level: int
    secret: str
    passphrase: str
    completed: bool


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


# ============== Arena Schemas ==============

class ArenaCombatantResponse(BaseModel):
    """Schema for an arena combatant's ranking entry."""
    rank: int
    combatant_id: str
    combatant_type: str
    level: int
    name: str
    title: str
    model_id: str = ""
    elo_rating: float
    wins: int
    losses: int
    total_battles: int
    win_rate: float

    class Config:
        from_attributes = True


class ArenaLeaderboardResponse(BaseModel):
    """Schema for an arena leaderboard."""
    combatant_type: Optional[str] = None
    entries: List[ArenaCombatantResponse]
    total: int


class ArenaBattleRoundResponse(BaseModel):
    """Schema for a single round in a battle."""
    round_number: int
    adversarial_message: str
    guardian_response: str
    leaked: bool = False


class ArenaSecretGuessResponse(BaseModel):
    """Schema for a secret guess."""
    guess_number: int
    guess: str
    correct: bool


class ArenaBattleSummaryResponse(BaseModel):
    """Brief summary of a battle (used in list views)."""
    battle_id: str
    timestamp: datetime
    guardian_id: str
    adversarial_id: str
    guardian_name: str
    adversarial_name: str
    guardian_level: int
    adversarial_level: int
    outcome: str
    total_turns: int
    total_guesses: int
    guardian_elo_before: Optional[float] = None
    guardian_elo_after: Optional[float] = None
    adversarial_elo_before: Optional[float] = None
    adversarial_elo_after: Optional[float] = None

    class Config:
        from_attributes = True


class ArenaBattleDetailResponse(ArenaBattleSummaryResponse):
    """Full detail of a battle including rounds and guesses."""
    secret_leaked_at_round: Optional[int] = None
    secret_guessed_at_attempt: Optional[int] = None
    max_turns: int = 10
    max_guesses: int = 3
    rounds: List[ArenaBattleRoundResponse] = []
    guesses: List[ArenaSecretGuessResponse] = []


class ArenaBattleListResponse(BaseModel):
    """Paginated list of battles."""
    battles: List[ArenaBattleSummaryResponse]
    total: int
    page: int
    per_page: int


class ArenaStatsResponse(BaseModel):
    """Schema for overall arena statistics."""
    total_battles: int
    total_combatants: int
    total_guardians: int
    total_adversarials: int


class OmbreInfoResponse(BaseModel):
    """Schema for a single adversarial (Ombre) character info."""
    level: int
    name: str
    title: str
    french_name: str
    difficulty: str
    color: str
    tagline: str


class OmbreListResponse(BaseModel):
    """Schema for all ombres."""
    ombres: List[OmbreInfoResponse]
    total: int


class OmbreChatMessage(BaseModel):
    """A single message from the game chat history."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class OmbreSuggestRequest(BaseModel):
    """Request body for getting a dynamic ombre suggestion."""
    adversarial_level: int = Field(..., ge=1, le=5, description="Which ombre (1-5) should suggest")
    guardian_level: int = Field(..., ge=1, le=5, description="The guardian level the user is playing")
    chat_history: List[OmbreChatMessage] = Field(
        default_factory=list,
        description="The user's current chat history with the guardian",
    )


class OmbreSuggestResponse(BaseModel):
    """Response from the ombre suggestion endpoint."""
    suggestion: str
    ombre_name: str
    ombre_level: int


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
