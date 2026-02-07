"""
Le Sésame Backend - Game Router

Main game endpoints for chat, passphrase verification, and progress tracking.

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from datetime import datetime
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db, User, GameRepository, LeaderboardRepository
from ..schemas import (
    ChatMessageRequest, ChatResponse, ModelConfig,
    PassphraseRequest, PassphraseResponse,
    GameProgressResponse, GameSessionResponse,
    LevelInfo, LevelCompletionDetails, LEVEL_CONFIGS
)
from ..services import get_level_keeper
from ..routers.auth import get_current_user, require_user
from ..core import logger

router = APIRouter()


def _build_level_info(config: LevelInfo, attempt=None) -> LevelInfo:
    """Build LevelInfo with attempt data."""
    return LevelInfo(
        level=config.level,
        name=config.name,
        description=config.description,
        difficulty=config.difficulty,
        security_mechanism=config.security_mechanism,
        hints=config.hints,
        completed=attempt.completed if attempt else False,
        attempts=attempt.attempts if attempt else 0,
        best_time=attempt.time_spent_seconds if attempt and attempt.completed else None
    )


@router.post("/session", response_model=GameSessionResponse)
async def create_session(
    user: Annotated[User, Depends(require_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create or get active game session."""
    repo = GameRepository(db)
    session = await repo.get_or_create_session(user)
    
    logger.info(f"Session retrieved/created for user {user.username}")
    
    return GameSessionResponse(
        session_id=session.session_token,
        current_level=session.current_level,
        started_at=session.started_at
    )


@router.post("/chat", response_model=ChatResponse)
async def send_message(
    request: ChatMessageRequest,
    user: Annotated[User, Depends(require_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the AI guardian at the specified level.
    
    The guardian will respond based on the level's security mechanism.
    """
    # Validate level
    if request.level < 1 or request.level > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid level. Must be between 1 and 5."
        )
    
    repo = GameRepository(db)
    
    # Get session and attempt
    session = await repo.get_or_create_session(user)
    attempt = await repo.get_or_create_level_attempt(session, request.level)
    
    # Get chat history
    chat_history = await repo.get_chat_history(session.id, request.level)
    
    # Get level keeper and process message
    keeper = get_level_keeper(request.level)

    # Build model_config dict from the optional request field
    model_config = (
        request.model_config_request.model_dump(exclude_none=True)
        if request.model_config_request
        else None
    )
    response_text, leaked = await keeper.process_message(
        request.message, chat_history, model_config=model_config
    )
    
    # Save conversation
    await repo.save_conversation(
        session_id=session.id,
        level=request.level,
        user_message=request.message,
        assistant_response=response_text,
        leaked_info=leaked
    )
    
    # Update attempt stats
    await repo.increment_messages(attempt)
    
    # Update session activity
    await repo.update_session_activity(session, request.level)
    
    logger.info(f"Chat message processed for user {user.username} at level {request.level}")
    
    return ChatResponse(
        message=request.message,
        response=response_text,
        level=request.level,
        attempts=attempt.attempts,
        messages_count=attempt.messages_sent  # already incremented above
    )


@router.post("/verify", response_model=PassphraseResponse)
async def verify_passphrase(
    request: PassphraseRequest,
    user: Annotated[User, Depends(require_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a secret attempt for the specified level.
    
    If correct, the level is marked complete.
    """
    # Validate level
    if request.level < 1 or request.level > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid level. Must be between 1 and 5."
        )
    
    game_repo = GameRepository(db)
    leaderboard_repo = LeaderboardRepository(db)
    
    # Get session and attempt
    session = await game_repo.get_or_create_session(user)
    attempt = await game_repo.get_or_create_level_attempt(session, request.level)
    
    # Increment attempts
    await game_repo.increment_attempt(attempt)
    
    # Get level keeper and verify
    keeper = get_level_keeper(request.level)
    is_correct = keeper.verify_secret(request.secret)
    
    if is_correct:
        # Mark level as complete
        if not attempt.completed:
            await game_repo.mark_level_completed(attempt)
            
            # Add to leaderboard
            await leaderboard_repo.create_entry(
                user_id=user.id,
                username=user.username,
                level=request.level,
                attempts=attempt.attempts,
                time_seconds=attempt.time_spent_seconds
            )
            
            logger.info(f"User {user.username} completed level {request.level}!")
        
        return PassphraseResponse(
            success=True,
            message="🎉 Congratulations! You've unlocked the secret!",
            level=request.level,
            secret=keeper.secret,
            next_level=request.level + 1 if request.level < 5 else None,
            time_spent=attempt.time_spent_seconds,
            attempts=attempt.attempts
        )
    else:
        return PassphraseResponse(
            success=False,
            message="❌ Incorrect secret. Keep trying!",
            level=request.level,
            attempts=attempt.attempts
        )


@router.get("/progress", response_model=GameProgressResponse)
async def get_progress(
    user: Annotated[User, Depends(require_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get the user's game progress across all levels."""
    repo = GameRepository(db)
    
    session = await repo.get_or_create_session(user)
    attempts = await repo.get_all_attempts(session.id)
    
    # Build level info list
    levels = []
    completed_levels = []
    total_attempts = 0
    total_time = 0.0
    
    for config in LEVEL_CONFIGS:
        attempt = attempts.get(config.level)
        level_info = _build_level_info(config, attempt)
        levels.append(level_info)
        
        if attempt:
            total_attempts += attempt.attempts
            if attempt.completed:
                completed_levels.append(config.level)
                total_time += attempt.time_spent_seconds
    
    return GameProgressResponse(
        current_level=session.current_level,
        completed_levels=completed_levels,
        total_attempts=total_attempts,
        total_time=total_time,
        levels=levels
    )


@router.get("/levels", response_model=List[LevelInfo])
async def get_levels(
    user: Annotated[Optional[User], Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get information about all levels."""
    if not user:
        return LEVEL_CONFIGS
    
    repo = GameRepository(db)
    
    # Get user's active session
    session = await repo.get_active_session(user.id)
    
    if not session:
        return LEVEL_CONFIGS
    
    # Get attempts
    attempts = await repo.get_all_attempts(session.id)
    
    # Build levels with user progress
    return [_build_level_info(config, attempts.get(config.level)) for config in LEVEL_CONFIGS]


@router.delete("/session")
async def reset_session(
    user: Annotated[User, Depends(require_user)],
    db: AsyncSession = Depends(get_db)
):
    """Reset the current game session (start over)."""
    repo = GameRepository(db)
    
    session = await repo.get_active_session(user.id)
    
    if session:
        await repo.deactivate_session(session)
        logger.info(f"Game session reset for user {user.username}")
    
    return {"message": "Session reset successfully"}


@router.get("/levels/{level}/completion", response_model=LevelCompletionDetails)
async def get_level_completion(
    level: int,
    user: Annotated[User, Depends(require_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get the secret and passphrase for a completed level."""
    if level < 1 or level > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid level. Must be between 1 and 5."
        )
    
    repo = GameRepository(db)
    session = await repo.get_active_session(user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found."
        )
    
    attempt = await repo.get_level_attempt(session.id, level)
    
    if not attempt or not attempt.completed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Level not completed yet. Complete the level first to see its secrets."
        )
    
    keeper = get_level_keeper(level)
    
    return LevelCompletionDetails(
        level=level,
        secret=keeper.secret,
        passphrase=keeper.passphrase,
        completed=True
    )


@router.get("/history/{level}")
async def get_chat_history_endpoint(
    level: int,
    user: Annotated[User, Depends(require_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a specific level."""
    if level < 1 or level > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid level"
        )
    
    repo = GameRepository(db)
    
    session = await repo.get_or_create_session(user)
    history = await repo.get_chat_history(session.id, level, limit=50)
    
    return {"level": level, "messages": history}
