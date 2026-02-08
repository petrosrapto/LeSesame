"""
Le Sésame Backend - Alembic Environment Configuration

This module configures Alembic to work with async SQLAlchemy and
automatically detect model changes for migrations.
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your models and database configuration
from app.db import Base
from app.db.models import (
    User, GameSession, LevelAttempt, ChatMessage, LeaderboardEntry, LevelSecret,
    ArenaCombatant, ArenaBattle,
)

# this is the Alembic Config object
config = context.config

# Get database URL from environment
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://le_sesame_user:le_sesame_password@localhost:5432/le_sesame"
)

# Set the sqlalchemy.url in the alembic config
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # For async migrations, we need to use the sync version of the URL
    # Convert asyncpg to psycopg2 for migrations
    sync_url = database_url.replace("+asyncpg", "+psycopg2")
    
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = sync_url
    
    from sqlalchemy import create_engine
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
