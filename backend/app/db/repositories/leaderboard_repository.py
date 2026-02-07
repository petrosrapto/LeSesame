"""
Le Sésame Backend - Leaderboard Repository

Repository for Leaderboard-related database operations.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from .base import BaseRepository
from ..models import LeaderboardEntry


class LeaderboardRepository(BaseRepository[LeaderboardEntry]):
    """Repository for Leaderboard entity operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, LeaderboardEntry)
    
    async def create_entry(
        self,
        user_id: int,
        username: str,
        level: int,
        attempts: int,
        time_seconds: float
    ) -> LeaderboardEntry:
        """Create a new leaderboard entry."""
        entry = LeaderboardEntry(
            user_id=user_id,
            username=username,
            level=level,
            attempts=attempts,
            time_seconds=time_seconds
        )
        return await self.create(entry)
    
    async def get_leaderboard(
        self,
        level: Optional[int] = None,
        timeframe: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[LeaderboardEntry], int]:
        """
        Get leaderboard entries with optional filters.
        
        Returns a tuple of (entries, total_count).
        """
        query = select(LeaderboardEntry)
        
        # Filter by level
        if level:
            query = query.where(LeaderboardEntry.level == level)
        
        # Filter by timeframe
        if timeframe == "weekly":
            week_ago = datetime.utcnow() - timedelta(days=7)
            query = query.where(LeaderboardEntry.completed_at >= week_ago)
        elif timeframe == "monthly":
            month_ago = datetime.utcnow() - timedelta(days=30)
            query = query.where(LeaderboardEntry.completed_at >= month_ago)
        
        # Order by level (desc), attempts (asc), time (asc)
        query = query.order_by(
            desc(LeaderboardEntry.level),
            LeaderboardEntry.attempts,
            LeaderboardEntry.time_seconds
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Paginate
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await self._session.execute(query)
        entries = list(result.scalars().all())
        
        return entries, total
    
    async def get_user_best_entry(
        self,
        user_id: int
    ) -> Optional[LeaderboardEntry]:
        """Get the user's best leaderboard entry (highest level, fewest attempts)."""
        result = await self._session.execute(
            select(LeaderboardEntry)
            .where(LeaderboardEntry.user_id == user_id)
            .order_by(
                desc(LeaderboardEntry.level),
                LeaderboardEntry.attempts,
                LeaderboardEntry.time_seconds
            )
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_user_entries(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[LeaderboardEntry]:
        """Get all leaderboard entries for a user."""
        result = await self._session.execute(
            select(LeaderboardEntry)
            .where(LeaderboardEntry.user_id == user_id)
            .order_by(desc(LeaderboardEntry.completed_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_level_ranking(
        self,
        level: int,
        limit: int = 10
    ) -> List[LeaderboardEntry]:
        """Get top entries for a specific level."""
        result = await self._session.execute(
            select(LeaderboardEntry)
            .where(LeaderboardEntry.level == level)
            .order_by(
                LeaderboardEntry.attempts,
                LeaderboardEntry.time_seconds
            )
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_level_leaderboard(
        self,
        level: int,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[LeaderboardEntry], int]:
        """Get paginated leaderboard for a specific level."""
        query = (
            select(LeaderboardEntry)
            .where(LeaderboardEntry.level == level)
            .order_by(
                LeaderboardEntry.attempts,
                LeaderboardEntry.time_seconds
            )
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Paginate
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await self._session.execute(query)
        entries = list(result.scalars().all())
        
        return entries, total
    
    async def get_top_players(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top players by highest level, fewest attempts, fastest time."""
        result = await self._session.execute(
            select(LeaderboardEntry)
            .order_by(
                desc(LeaderboardEntry.level),
                LeaderboardEntry.attempts,
                LeaderboardEntry.time_seconds
            )
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_stats(self) -> dict:
        """Get overall leaderboard statistics."""
        # Total completions
        total_result = await self._session.execute(
            select(func.count(LeaderboardEntry.id))
        )
        total_completions = total_result.scalar() or 0
        
        # Unique players
        unique_result = await self._session.execute(
            select(func.count(func.distinct(LeaderboardEntry.user_id)))
        )
        unique_players = unique_result.scalar() or 0
        
        # Stats per level
        level_stats = []
        for level in range(1, 6):
            count_result = await self._session.execute(
                select(func.count(LeaderboardEntry.id))
                .where(LeaderboardEntry.level == level)
            )
            count = count_result.scalar() or 0
            
            avg_attempts_result = await self._session.execute(
                select(func.avg(LeaderboardEntry.attempts))
                .where(LeaderboardEntry.level == level)
            )
            avg_attempts = avg_attempts_result.scalar() or 0
            
            avg_time_result = await self._session.execute(
                select(func.avg(LeaderboardEntry.time_seconds))
                .where(LeaderboardEntry.level == level)
            )
            avg_time = avg_time_result.scalar() or 0
            
            level_stats.append({
                "level": level,
                "completions": count,
                "avg_attempts": round(float(avg_attempts), 1),
                "avg_time_seconds": round(float(avg_time), 1)
            })
        
        return {
            "total_completions": total_completions,
            "unique_players": unique_players,
            "level_stats": level_stats
        }
