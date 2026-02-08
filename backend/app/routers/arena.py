"""
Le Sésame Backend - Arena Router

API endpoints for the adversarial arena: leaderboards and battle history.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..db.repositories.arena_repository import ArenaRepository
from ..schemas import (
    ArenaCombatantResponse,
    ArenaLeaderboardResponse,
    ArenaStatsResponse,
    ArenaBattleSummaryResponse,
    ArenaBattleDetailResponse,
    ArenaBattleListResponse,
    ArenaBattleRoundResponse,
    ArenaSecretGuessResponse,
    OmbreInfoResponse,
    OmbreListResponse,
    OmbreSuggestRequest,
    OmbreSuggestResponse,
)
from ..services.adversarials.factory import ADVERSARIAL_INFO, get_adversarial_agent
from ..services.adversarials.base import AdversarialActionType
from ..core import logger

router = APIRouter()


@router.get("/stats", response_model=ArenaStatsResponse)
async def get_arena_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get overall arena statistics.

    Returns total battles played, total AI combatants,
    and the breakdown of guardians vs adversarials.
    """
    repo = ArenaRepository(db)
    stats = await repo.get_stats()
    return ArenaStatsResponse(**stats)


@router.get("/leaderboard", response_model=ArenaLeaderboardResponse)
async def get_arena_leaderboard(
    type: Optional[str] = Query(
        None,
        pattern="^(guardian|adversarial)$",
        description="Filter by combatant type: 'guardian' or 'adversarial'",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the arena leaderboard ranked by ELO rating.

    Use ``?type=guardian`` for the Guardian leaderboard (Les Gardiens)
    and ``?type=adversarial`` for the Adversarial leaderboard (Les Ombres).
    Omit the parameter to see all combatants together.
    """
    repo = ArenaRepository(db)
    entries = await repo.get_rankings(combatant_type=type)

    combatant_responses = [
        ArenaCombatantResponse(
            rank=idx + 1,
            combatant_id=e.combatant_id,
            combatant_type=e.combatant_type,
            level=e.level,
            name=e.name,
            title=e.title,
            model_id=e.model_id,
            elo_rating=e.elo_rating,
            wins=e.wins,
            losses=e.losses,
            total_battles=e.total_battles,
            win_rate=(e.wins / e.total_battles * 100.0) if e.total_battles > 0 else 0.0,
        )
        for idx, e in enumerate(entries)
    ]

    return ArenaLeaderboardResponse(
        combatant_type=type,
        entries=combatant_responses,
        total=len(combatant_responses),
    )


@router.get("/battles", response_model=ArenaBattleListResponse)
async def get_arena_battles(
    combatant_id: Optional[str] = Query(
        None,
        description="Filter battles by combatant id (e.g. 'guardian_L1', 'adversarial_L3')",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated battle history.

    Optionally filter to battles involving a specific combatant.
    """
    repo = ArenaRepository(db)
    battles, total = await repo.get_battles(
        combatant_id=combatant_id,
        page=page,
        per_page=per_page,
    )

    battle_summaries = [
        ArenaBattleSummaryResponse(
            battle_id=b.battle_id,
            timestamp=b.timestamp,
            guardian_id=b.guardian_id,
            adversarial_id=b.adversarial_id,
            guardian_name=b.guardian_name,
            adversarial_name=b.adversarial_name,
            guardian_level=b.guardian_level,
            adversarial_level=b.adversarial_level,
            outcome=b.outcome,
            total_turns=b.total_turns,
            total_guesses=b.total_guesses,
            guardian_elo_before=b.guardian_elo_before,
            guardian_elo_after=b.guardian_elo_after,
            adversarial_elo_before=b.adversarial_elo_before,
            adversarial_elo_after=b.adversarial_elo_after,
        )
        for b in battles
    ]

    return ArenaBattleListResponse(
        battles=battle_summaries,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/battles/{battle_id}", response_model=ArenaBattleDetailResponse)
async def get_arena_battle_detail(
    battle_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed view of a specific battle, including rounds and guesses."""
    repo = ArenaRepository(db)
    battle = await repo.get_battle(battle_id)

    if not battle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Battle {battle_id} not found",
        )

    # Parse stored JSON
    rounds = []
    if battle.rounds_json:
        try:
            for r in json.loads(battle.rounds_json):
                rounds.append(ArenaBattleRoundResponse(**r))
        except (json.JSONDecodeError, KeyError):
            pass

    guesses = []
    if battle.guesses_json:
        try:
            for g in json.loads(battle.guesses_json):
                guesses.append(ArenaSecretGuessResponse(**g))
        except (json.JSONDecodeError, KeyError):
            pass

    return ArenaBattleDetailResponse(
        battle_id=battle.battle_id,
        timestamp=battle.timestamp,
        guardian_id=battle.guardian_id,
        adversarial_id=battle.adversarial_id,
        guardian_name=battle.guardian_name,
        adversarial_name=battle.adversarial_name,
        guardian_level=battle.guardian_level,
        adversarial_level=battle.adversarial_level,
        outcome=battle.outcome,
        total_turns=battle.total_turns,
        total_guesses=battle.total_guesses,
        guardian_elo_before=battle.guardian_elo_before,
        guardian_elo_after=battle.guardian_elo_after,
        adversarial_elo_before=battle.adversarial_elo_before,
        adversarial_elo_after=battle.adversarial_elo_after,
        secret_leaked_at_round=battle.secret_leaked_at_round,
        secret_guessed_at_attempt=battle.secret_guessed_at_attempt,
        max_turns=battle.max_turns,
        max_guesses=battle.max_guesses,
        rounds=rounds,
        guesses=guesses,
    )


@router.get("/ombres", response_model=OmbreListResponse)
async def get_ombres():
    """
    Get the list of adversarial characters (Les Ombres / The Shadows).

    Returns metadata for all 5 adversarial agents that can be used
    to suggest attack strategies to players.
    """
    ombres = [
        OmbreInfoResponse(
            level=level,
            name=info["name"],
            title=info["title"],
            french_name=info["french_name"],
            difficulty=info["difficulty"],
            color=info["color"],
            tagline=info["tagline"],
        )
        for level, info in sorted(ADVERSARIAL_INFO.items())
    ]

    return OmbreListResponse(ombres=ombres, total=len(ombres))


@router.post("/ombres/suggest", response_model=OmbreSuggestResponse)
async def get_ombre_suggestion(
    request: OmbreSuggestRequest,
):
    """
    Get a dynamic attack suggestion from an Ombre.

    Sends the current game chat history to the chosen adversarial agent,
    which generates the next attack message it would use against the guardian.
    The user can then copy or use that suggestion in their own words.
    """
    adv_level = request.adversarial_level

    # Map game chat roles to adversarial conversation roles.
    # The user's messages are what the adversarial "already said",
    # and the assistant responses are what the guardian said.
    arena_history = []
    for msg in request.chat_history:
        if msg.role == "user":
            arena_history.append({"role": "adversarial", "content": msg.content})
        elif msg.role == "assistant":
            arena_history.append({"role": "guardian", "content": msg.content})

    turn_number = len([m for m in arena_history if m["role"] == "adversarial"]) + 1

    try:
        agent = get_adversarial_agent(adv_level)
        action = await agent.generate_attack(
            chat_history=arena_history,
            turn_number=turn_number,
            max_turns=20,       # generous limit — this is a suggestion
            guesses_remaining=0, # don't let the agent guess
        )

        # If the adversarial returned a guess instead of a message,
        # convert it into a user-friendly suggestion.
        if action.action_type == AdversarialActionType.GUESS:
            action_content = f"Try submitting **{action.content}** as the secret."
        else:
            action_content = action.content

        info = ADVERSARIAL_INFO.get(adv_level, {})
        return OmbreSuggestResponse(
            suggestion=action_content,
            ombre_name=info.get("name", f"Level {adv_level}"),
            ombre_level=adv_level,
        )
    except Exception as e:
        logger.error(f"Ombre suggestion failed for level {adv_level}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate ombre suggestion. Please try again.",
        )
