"""
Le Sésame Backend - Arena Module

Battle engine, ELO rating system, and leaderboard for
adversarial vs. guardian evaluation.
"""

from .engine import ArenaEngine
from .elo import EloRatingSystem
from .leaderboard import Leaderboard
from .models import (
    BattleResult,
    BattleRound,
    BattleConfig,
    Combatant,
    CombatantType,
    LeaderboardEntry,
)

__all__ = [
    "ArenaEngine",
    "EloRatingSystem",
    "Leaderboard",
    "BattleResult",
    "BattleRound",
    "BattleConfig",
    "Combatant",
    "CombatantType",
    "LeaderboardEntry",
]
