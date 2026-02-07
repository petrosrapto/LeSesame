"""
Le Sésame Backend - Base Repository

Abstract base class for all repositories.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from abc import ABC
from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository providing common CRUD operations.
    
    All repositories should inherit from this class and specify their model type.
    """
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self._session = session
        self._model = model
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Get a single record by ID."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records with pagination."""
        result = await self._session.execute(
            select(self._model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
    
    async def create(self, entity: T) -> T:
        """Create a new record."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def update(self, entity: T) -> T:
        """Update an existing record."""
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def delete(self, entity: T) -> None:
        """Delete a record."""
        await self._session.delete(entity)
        await self._session.flush()
