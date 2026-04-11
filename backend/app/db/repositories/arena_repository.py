"""
Le Sésame Backend - Arena Repository

Repository for Arena-related database operations (combatants, battles).

Author: Petros Raptopoulos
Date: 2026/02/08
"""

import json
from datetime import datetime
from typing import Optional, List, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_

from .base import BaseRepository
from ..models import ArenaCombatant, ArenaBattle


class ArenaRepository(BaseRepository[ArenaCombatant]):
    """Repository for Arena entity operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ArenaCombatant)

    # ── Combatant operations ──────────────────────────────────────────

    async def get_combatant(self, combatant_id: str) -> Optional[ArenaCombatant]:
        """Get a combatant by its unique combatant_id string."""
        result = await self._session.execute(
            select(ArenaCombatant).where(
                ArenaCombatant.combatant_id == combatant_id
            )
        )
        return result.scalar_one_or_none()

    async def upsert_combatant(
        self,
        combatant_id: str,
        combatant_type: str,
        level: int,
        name: str,
        title: str,
        model_id: str = "default",
        elo_rating: float = 1500.0,
    ) -> ArenaCombatant:
        """Create or update a combatant entry."""
        existing = await self.get_combatant(combatant_id)
        if existing:
            existing.name = name
            existing.title = title
            return await self.update(existing)

        entry = ArenaCombatant(
            combatant_id=combatant_id,
            combatant_type=combatant_type,
            level=level,
            name=name,
            title=title,
            model_id=model_id,
            elo_rating=elo_rating,
        )
        return await self.create(entry)

    async def get_rankings(
        self,
        combatant_type: Optional[str] = None,
    ) -> List[ArenaCombatant]:
        """
        Get combatants ranked by ELO (descending).

        Args:
            combatant_type: ``"guardian"`` or ``"adversarial"``; *None* for all.
        """
        query = select(ArenaCombatant)
        if combatant_type:
            query = query.where(ArenaCombatant.combatant_type == combatant_type)
        query = query.order_by(desc(ArenaCombatant.elo_rating))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update_after_battle(
        self,
        combatant_id: str,
        new_elo: float,
        won: bool,
    ) -> None:
        """Update a combatant's stats after a battle."""
        entry = await self.get_combatant(combatant_id)
        if not entry:
            return
        entry.elo_rating = new_elo
        entry.total_battles += 1
        if won:
            entry.wins += 1
        else:
            entry.losses += 1
        await self.update(entry)

    async def set_validation_result(
        self,
        combatant_id: str,
        passed: bool,
    ) -> None:
        """Store the validation outcome for a combatant."""
        entry = await self.get_combatant(combatant_id)
        if not entry:
            return
        entry.validated = True
        entry.validation_passed = passed
        entry.validated_at = datetime.utcnow()
        await self.update(entry)

    # ── Battle operations ─────────────────────────────────────────────

    async def create_battle(self, battle: ArenaBattle) -> ArenaBattle:
        """Persist a new battle result."""
        self._session.add(battle)
        await self._session.flush()
        await self._session.refresh(battle)
        return battle

    async def get_battle(self, battle_id: str) -> Optional[ArenaBattle]:
        """Get a battle by its UUID."""
        result = await self._session.execute(
            select(ArenaBattle).where(ArenaBattle.battle_id == battle_id)
        )
        return result.scalar_one_or_none()

    async def get_battles(
        self,
        combatant_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[ArenaBattle], int]:
        """
        Get battle history with optional combatant filter and pagination.

        Returns ``(battles, total_count)``.
        """
        query = select(ArenaBattle)
        if combatant_id:
            query = query.where(
                or_(
                    ArenaBattle.guardian_id == combatant_id,
                    ArenaBattle.adversarial_id == combatant_id,
                )
            )
        query = query.order_by(desc(ArenaBattle.timestamp))

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        result = await self._session.execute(query)
        battles = list(result.scalars().all())

        return battles, total

    async def get_stats(self) -> dict:
        """Return aggregate arena statistics."""
        # Total battles
        result = await self._session.execute(
            select(func.count()).select_from(ArenaBattle)
        )
        total_battles = result.scalar() or 0

        # Total combatants
        result = await self._session.execute(
            select(func.count()).select_from(ArenaCombatant)
        )
        total_combatants = result.scalar() or 0

        # Guardians count
        result = await self._session.execute(
            select(func.count()).select_from(ArenaCombatant).where(
                ArenaCombatant.combatant_type == "guardian"
            )
        )
        total_guardians = result.scalar() or 0

        # Adversarials count
        result = await self._session.execute(
            select(func.count()).select_from(ArenaCombatant).where(
                ArenaCombatant.combatant_type == "adversarial"
            )
        )
        total_adversarials = result.scalar() or 0

        return {
            "total_battles": total_battles,
            "total_combatants": total_combatants,
            "total_guardians": total_guardians,
            "total_adversarials": total_adversarials,
        }

    async def get_matchup_counts(self) -> Dict[tuple, int]:
        """
        Return the number of battles played for every (adversarial_id, guardian_id) pair.

        Returns:
            ``{("adversarial_L1", "guardian_L2"): 3, ...}``
        """
        stmt = (
            select(
                ArenaBattle.adversarial_id,
                ArenaBattle.guardian_id,
                func.count().label("cnt"),
            )
            .group_by(ArenaBattle.adversarial_id, ArenaBattle.guardian_id)
        )
        result = await self._session.execute(stmt)
        return {
            (row.adversarial_id, row.guardian_id): row.cnt
            for row in result.all()
        }
