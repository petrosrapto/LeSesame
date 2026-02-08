"""
Le Sésame Backend - Arena Data Models

Data models for the battle engine, results, and leaderboard.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class CombatantType(str, Enum):
    """Type of combatant in the arena."""
    GUARDIAN = "guardian"
    ADVERSARIAL = "adversarial"


class Combatant(BaseModel):
    """Represents a combatant (guardian or adversarial) in the arena.

    A player is uniquely identified by (type, level, model_id) — the same
    level definition with a different LLM model is a different player.
    """

    type: CombatantType
    level: int = Field(ge=1, le=5)
    name: str
    title: str
    model_id: str = Field(
        description="LLM model identifier (e.g. 'gpt-4o', 'mistral-small-latest').",
    )
    model_config_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="LLM model configuration used by this combatant.",
    )

    @property
    def combatant_id(self) -> str:
        """Unique identifier combining type, level, and model."""
        return f"{self.type.value}_L{self.level}_{self.model_id}"

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        return f"{self.name}, {self.title} (L{self.level}) [{self.model_id}]"


class BattleRound(BaseModel):
    """A single round (adversarial question + guardian response) in a battle."""

    round_number: int
    adversarial_message: str
    guardian_response: str
    leaked: bool = Field(
        default=False,
        description="Whether the guardian leaked the secret in this round.",
    )


class SecretGuess(BaseModel):
    """An adversarial's guess at the secret."""

    guess_number: int
    guess: str
    correct: bool


class BattleConfig(BaseModel):
    """Configuration for a battle."""

    max_turns: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of adversarial turns.",
    )
    max_guesses: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of secret guesses during conversation.",
    )
    guardian_level: int = Field(ge=1, le=5)
    adversarial_level: int = Field(ge=1, le=5)
    guardian_model_config: Optional[Dict[str, Any]] = None
    adversarial_model_config: Optional[Dict[str, Any]] = None
    secret: Optional[str] = Field(
        default=None,
        description="Override the default secret for this battle.",
    )
    passphrase: Optional[str] = Field(
        default=None,
        description="Override the default passphrase for this battle.",
    )


class BattleOutcome(str, Enum):
    """Outcome of a battle."""
    ADVERSARIAL_WIN_GUESS = "adversarial_win_guess"     # Adversarial guessed correctly
    GUARDIAN_WIN = "guardian_win"                         # Secret was protected


class BattleResult(BaseModel):
    """Complete result of a battle between adversarial and guardian."""

    battle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Combatants
    guardian: Combatant
    adversarial: Combatant

    # Configuration
    config: BattleConfig

    # Battle details
    rounds: List[BattleRound] = Field(default_factory=list)
    guesses: List[SecretGuess] = Field(default_factory=list)
    total_turns: int = 0

    # Outcome
    outcome: BattleOutcome = BattleOutcome.GUARDIAN_WIN
    secret_leaked_at_round: Optional[int] = None
    secret_guessed_at_attempt: Optional[int] = None

    # The actual secret (for records)
    actual_secret: str = ""

    # ELO changes (filled in after rating calculation)
    guardian_elo_before: Optional[float] = None
    guardian_elo_after: Optional[float] = None
    adversarial_elo_before: Optional[float] = None
    adversarial_elo_after: Optional[float] = None

    @property
    def adversarial_won(self) -> bool:
        """Whether the adversarial won (guessed the secret correctly)."""
        return self.outcome == BattleOutcome.ADVERSARIAL_WIN_GUESS

    @property
    def guardian_won(self) -> bool:
        """Whether the guardian won (protected the secret)."""
        return self.outcome == BattleOutcome.GUARDIAN_WIN

    def summary(self) -> str:
        """Human-readable battle summary."""
        winner = self.adversarial.display_name if self.adversarial_won else self.guardian.display_name
        loser = self.guardian.display_name if self.adversarial_won else self.adversarial.display_name

        lines = [
            f"═══ Battle Report ═══",
            f"ID: {self.battle_id[:8]}",
            f"Guardian:    {self.guardian.display_name}",
            f"Adversarial: {self.adversarial.display_name}",
            f"Turns: {self.total_turns}/{self.config.max_turns}",
            f"Guesses: {len(self.guesses)}/{self.config.max_guesses}",
            f"Outcome: {self.outcome.value}",
            f"Winner: {winner}",
        ]

        if self.secret_leaked_at_round is not None:
            lines.append(f"Secret leaked at round: {self.secret_leaked_at_round}")
        if self.secret_guessed_at_attempt is not None:
            lines.append(f"Secret guessed at attempt: {self.secret_guessed_at_attempt}")

        if self.guardian_elo_before is not None:
            lines.extend([
                f"Guardian ELO: {self.guardian_elo_before:.0f} → {self.guardian_elo_after:.0f} ({self.guardian_elo_after - self.guardian_elo_before:+.0f})",
                f"Adversarial ELO: {self.adversarial_elo_before:.0f} → {self.adversarial_elo_after:.0f} ({self.adversarial_elo_after - self.adversarial_elo_before:+.0f})",
            ])

        return "\n".join(lines)


class LeaderboardEntry(BaseModel):
    """A single entry in the leaderboard."""

    combatant_id: str
    combatant_type: CombatantType
    level: int
    name: str
    title: str
    model_id: str = ""
    elo_rating: float = 1500.0
    wins: int = 0
    losses: int = 0
    total_battles: int = 0

    @property
    def win_rate(self) -> float:
        """Win rate as a percentage."""
        if self.total_battles == 0:
            return 0.0
        return (self.wins / self.total_battles) * 100.0
