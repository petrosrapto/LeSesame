"""
Le Sésame Backend - Leaderboard Router

Leaderboard endpoints for viewing rankings.

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db, LeaderboardRepository
from ..schemas import LeaderboardResponse, LeaderboardEntryResponse
from ..core import logger

router = APIRouter()


@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard(
    level: Optional[int] = Query(None, ge=1, le=20, description="Filter by level"),
    timeframe: Optional[str] = Query(None, pattern="^(weekly|monthly|all)$", description="Time filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the leaderboard rankings.
    
    Can filter by level and timeframe (weekly, monthly, all).
    Ranked by: level completed (desc), fewest attempts, fastest time.
    """
    repo = LeaderboardRepository(db)
    entries, total = await repo.get_leaderboard(
        level=level,
        timeframe=timeframe,
        page=page,
        per_page=per_page
    )
    
    # Build response with ranks
    offset = (page - 1) * per_page
    leaderboard_entries = [
        LeaderboardEntryResponse(
            rank=offset + idx + 1,
            username=entry.username,
            level=entry.level,
            attempts=entry.attempts,
            time_seconds=entry.time_seconds,
            completed_at=entry.completed_at
        )
        for idx, entry in enumerate(entries)
    ]
    
    return LeaderboardResponse(
        entries=leaderboard_entries,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/top")
async def get_top_players(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top players by highest level completed with best stats.
    """
    repo = LeaderboardRepository(db)
    entries = await repo.get_top_players(limit=limit)
    
    return {
        "top_players": [
            {
                "rank": idx + 1,
                "username": entry.username,
                "level": entry.level,
                "attempts": entry.attempts,
                "time_seconds": round(entry.time_seconds, 2),
                "completed_at": entry.completed_at.isoformat()
            }
            for idx, entry in enumerate(entries)
        ]
    }


@router.get("/stats")
async def get_leaderboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall leaderboard statistics.
    """
    repo = LeaderboardRepository(db)
    return await repo.get_stats()


@router.get("/level/{level}")
async def get_level_leaderboard(
    level: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get leaderboard for a specific level.
    Ranked by fewest attempts, then fastest time.
    """
    if level < 1 or level > 20:
        return {"error": "Invalid level"}
    
    repo = LeaderboardRepository(db)
    entries, total = await repo.get_level_leaderboard(
        level=level,
        page=page,
        per_page=per_page
    )
    
    offset = (page - 1) * per_page
    
    return {
        "level": level,
        "entries": [
            {
                "rank": offset + idx + 1,
                "username": entry.username,
                "attempts": entry.attempts,
                "time_seconds": round(entry.time_seconds, 2),
                "completed_at": entry.completed_at.isoformat()
            }
            for idx, entry in enumerate(entries)
        ],
        "total": total,
        "page": page,
        "per_page": per_page
    }
