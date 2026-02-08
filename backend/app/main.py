"""
Le Sésame Backend - Main Application Entry Point

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core import settings, logger
from .db import init_db
from .routers import game, auth, leaderboard, health, arena, admin


def _configure_langsmith() -> None:
    """
    Propagate LangSmith settings into the environment so that
    LangChain automatically sends traces to LangSmith.
    """
    if settings.langchain_tracing_v2.lower() == "true" and settings.langchain_api_key:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", settings.langchain_tracing_v2)
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
        os.environ.setdefault("LANGCHAIN_ENDPOINT", settings.langchain_endpoint)
        logger.info(f"LangSmith tracing enabled — project={settings.langchain_project}")
    else:
        logger.info("LangSmith tracing disabled (LANGCHAIN_TRACING_V2 != true or no API key)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info("Starting Le Sésame backend...")
    _configure_langsmith()
    await init_db()
    logger.info(f"Server running on {settings.host}:{settings.port}")
    yield
    # Shutdown
    logger.info("Shutting down Le Sésame backend...")


app = FastAPI(
    title="Le Sésame API",
    description="""
    🔐 **Le Sésame** - The Multi-Level Secret Keeper Game API
    
    Test your skills against AI guardians protecting secrets at increasing difficulty levels.
    
    ## Features
    - 5 progressive difficulty levels
    - Chat-based interaction with AI guardians
    - Passphrase verification system
    - Global leaderboard
    - Progress tracking
    """,
    version="1.0.0",
    contact={
        "name": "Petros Raptopoulos",
        "email": "petros.raptopoulos@example.com",
    },
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(game.router, prefix="/api/game", tags=["Game"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["Leaderboard"])
app.include_router(arena.router, prefix="/api/arena", tags=["Arena"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Le Sésame API",
        "version": "1.0.0",
        "description": "Multi-Level Secret Keeper Game",
        "docs": "/docs",
        "health": "/health"
    }
