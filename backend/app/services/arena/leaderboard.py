"""
Le Sésame Backend - Leaderboard

Manages the leaderboard: tracks combatant ratings, records battle
results, and produces rankings.

Persists to PostgreSQL via async SQLAlchemy.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

from __future__ import annotations

import json
from typing import List, Optional, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    BattleResult,
    CombatantType,
    LeaderboardEntry,
)
from .elo import EloRatingSystem

# Guardian & adversarial metadata for initialization
from .engine import GUARDIAN_INFO
from ..adversarials.factory import ADVERSARIAL_INFO

# DB models & repository
from ...db.models import ArenaCombatant, ArenaBattle
from ...db.repositories.arena_repository import ArenaRepository


DEFAULT_ELO = 1500.0


class Leaderboard:
    """
    Manages ELO ratings and battle history for all combatants.

    Persists data to the database via :class:`ArenaRepository`.
    """

    def __init__(
        self,
        session: AsyncSession,
        k_factor: float = 32.0,
    ):
        """
        Initialize the leaderboard.

        Args:
            session: Active async database session.
            k_factor: ELO K-factor for rating calculations.
        """
        self.session = session
        self.repo = ArenaRepository(session)
        self.elo_system = EloRatingSystem(k_factor=k_factor)

    async def ensure_combatants(self, model_id: str = "default") -> None:
        """
        Ensure all known combatants exist in the database for a given model.

        Args:
            model_id: The LLM model identifier to register combatants for.
        """
        # Guardians
        for level, info in GUARDIAN_INFO.items():
            cid = f"guardian_L{level}_{model_id}"
            await self.repo.upsert_combatant(
                combatant_id=cid,
                combatant_type=CombatantType.GUARDIAN.value,
                level=level,
                name=info["name"],
                title=info["title"],
                model_id=model_id,
                elo_rating=DEFAULT_ELO,
            )

        # Adversarials
        for level, info in ADVERSARIAL_INFO.items():
            cid = f"adversarial_L{level}_{model_id}"
            await self.repo.upsert_combatant(
                combatant_id=cid,
                combatant_type=CombatantType.ADVERSARIAL.value,
                level=level,
                name=info["name"],
                title=info["title"],
                model_id=model_id,
                elo_rating=DEFAULT_ELO,
            )

    async def record_battle(self, result: BattleResult) -> BattleResult:
        """
        Record a battle result, update ELO ratings, and persist.

        Args:
            result: The battle result to record.

        Returns:
            The updated battle result with ELO changes filled in.
        """
        adv_id = result.adversarial.combatant_id
        guard_id = result.guardian.combatant_id

        # Auto-register combatants if they don't exist yet
        adv_entry = await self.repo.get_combatant(adv_id)
        if not adv_entry:
            adv_entry = await self.repo.upsert_combatant(
                combatant_id=adv_id,
                combatant_type=result.adversarial.type.value,
                level=result.adversarial.level,
                name=result.adversarial.name,
                title=result.adversarial.title,
                model_id=result.adversarial.model_id,
                elo_rating=DEFAULT_ELO,
            )

        guard_entry = await self.repo.get_combatant(guard_id)
        if not guard_entry:
            guard_entry = await self.repo.upsert_combatant(
                combatant_id=guard_id,
                combatant_type=result.guardian.type.value,
                level=result.guardian.level,
                name=result.guardian.name,
                title=result.guardian.title,
                model_id=result.guardian.model_id,
                elo_rating=DEFAULT_ELO,
            )

        # Store pre-battle ratings
        result.adversarial_elo_before = adv_entry.elo_rating
        result.guardian_elo_before = guard_entry.elo_rating

        # Calculate new ratings
        new_adv_elo, new_guard_elo = self.elo_system.calculate_new_ratings(
            adversarial_rating=adv_entry.elo_rating,
            guardian_rating=guard_entry.elo_rating,
            result=result,
        )

        # Store post-battle ratings
        result.adversarial_elo_after = new_adv_elo
        result.guardian_elo_after = new_guard_elo

        # Update combatant stats in DB
        await self.repo.update_after_battle(
            combatant_id=adv_id,
            new_elo=new_adv_elo,
            won=result.adversarial_won,
        )
        await self.repo.update_after_battle(
            combatant_id=guard_id,
            new_elo=new_guard_elo,
            won=result.guardian_won,
        )

        # Persist the battle itself
        battle = ArenaBattle(
            battle_id=result.battle_id,
            timestamp=result.timestamp,
            guardian_id=guard_id,
            adversarial_id=adv_id,
            guardian_level=result.guardian.level,
            adversarial_level=result.adversarial.level,
            guardian_name=result.guardian.display_name,
            adversarial_name=result.adversarial.display_name,
            outcome=result.outcome.value,
            total_turns=result.total_turns,
            total_guesses=len(result.guesses),
            secret_leaked_at_round=result.secret_leaked_at_round,
            secret_guessed_at_attempt=result.secret_guessed_at_attempt,
            guardian_elo_before=result.guardian_elo_before,
            guardian_elo_after=result.guardian_elo_after,
            adversarial_elo_before=result.adversarial_elo_before,
            adversarial_elo_after=result.adversarial_elo_after,
            max_turns=result.config.max_turns,
            max_guesses=result.config.max_guesses,
            rounds_json=json.dumps(
                [r.model_dump() for r in result.rounds]
            ),
            guesses_json=json.dumps(
                [g.model_dump() for g in result.guesses]
            ),
        )
        await self.repo.create_battle(battle)

        return result

    async def get_rankings(
        self,
        combatant_type: Optional[CombatantType] = None,
    ) -> List[LeaderboardEntry]:
        """
        Get ranked leaderboard entries.

        Args:
            combatant_type: Filter by type (GUARDIAN or ADVERSARIAL).
                           None returns all combatants.

        Returns:
            List of Pydantic entries sorted by ELO rating (descending).
        """
        ct = combatant_type.value if combatant_type else None
        db_entries = await self.repo.get_rankings(combatant_type=ct)
        return [
            LeaderboardEntry(
                combatant_id=e.combatant_id,
                combatant_type=CombatantType(e.combatant_type),
                level=e.level,
                name=e.name,
                title=e.title,
                model_id=e.model_id,
                elo_rating=e.elo_rating,
                wins=e.wins,
                losses=e.losses,
                total_battles=e.total_battles,
            )
            for e in db_entries
        ]

    async def get_entry(self, combatant_id: str) -> Optional[LeaderboardEntry]:
        """Get a specific combatant's leaderboard entry."""
        e = await self.repo.get_combatant(combatant_id)
        if not e:
            return None
        return LeaderboardEntry(
            combatant_id=e.combatant_id,
            combatant_type=CombatantType(e.combatant_type),
            level=e.level,
            name=e.name,
            title=e.title,
            model_id=e.model_id,
            elo_rating=e.elo_rating,
            wins=e.wins,
            losses=e.losses,
            total_battles=e.total_battles,
        )

    async def get_battle_history(
        self,
        combatant_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Get battle history, optionally filtered by combatant.

        Args:
            combatant_id: Filter to battles involving this combatant.
            limit: Maximum number of records to return.

        Returns:
            List of battle history records (most recent first).
        """
        battles, _ = await self.repo.get_battles(
            combatant_id=combatant_id,
            page=1,
            per_page=limit,
        )
        return [
            {
                "battle_id": b.battle_id,
                "timestamp": b.timestamp.isoformat() if b.timestamp else None,
                "adversarial": b.adversarial_id,
                "guardian": b.guardian_id,
                "outcome": b.outcome,
                "turns": b.total_turns,
                "adversarial_elo": b.adversarial_elo_after,
                "guardian_elo": b.guardian_elo_after,
            }
            for b in battles
        ]

    async def reset(self) -> None:
        """Reset all ratings and history."""
        # Delete all battles
        from sqlalchemy import delete
        await self.session.execute(delete(ArenaBattle))
        await self.session.execute(delete(ArenaCombatant))
        await self.session.flush()

        # Re-seed combatants
        await self.ensure_combatants()

    async def display_rankings(
        self,
        combatant_type: Optional[CombatantType] = None,
    ) -> str:
        """
        Format rankings as a human-readable table.

        Args:
            combatant_type: Filter by type.

        Returns:
            Formatted ranking table string.
        """
        entries = await self.get_rankings(combatant_type)
        type_label = combatant_type.value.upper() if combatant_type else "ALL"

        lines = [
            f"\n{'═' * 100}",
            f"  LE SÉSAME ARENA — {type_label} LEADERBOARD",
            f"{'═' * 100}",
            f"{'Rank':<6}{'Name':<30}{'Model':<25}{'ELO':>8}{'W':>6}{'L':>6}{'Total':>7}{'Win%':>8}",
            f"{'─' * 100}",
        ]

        for i, entry in enumerate(entries, 1):
            model_short = (entry.model_id[:22] + "..") if len(entry.model_id) > 24 else entry.model_id
            lines.append(
                f"{i:<6}"
                f"{entry.name + ', ' + entry.title:<30}"
                f"{model_short:<25}"
                f"{entry.elo_rating:>8.0f}"
                f"{entry.wins:>6}"
                f"{entry.losses:>6}"
                f"{entry.total_battles:>7}"
                f"{entry.win_rate:>7.1f}%"
            )

        lines.append(f"{'═' * 100}\n")
        return "\n".join(lines)
