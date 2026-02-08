"""Add arena tables (arena_combatants, arena_battles)

Revision ID: 002_arena_tables
Revises: 001_initial
Create Date: 2026-02-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_arena_tables'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create arena_combatants table
    op.create_table(
        'arena_combatants',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('combatant_id', sa.String(length=150), nullable=False),
        sa.Column('combatant_type', sa.String(length=20), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('model_id', sa.String(length=100), nullable=False, server_default='default'),
        sa.Column('elo_rating', sa.Float(), nullable=False, server_default='1500.0'),
        sa.Column('wins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('losses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_battles', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_arena_combatants_combatant_id'),
        'arena_combatants',
        ['combatant_id'],
        unique=True,
    )

    # Create arena_battles table
    op.create_table(
        'arena_battles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('battle_id', sa.String(length=36), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        # Combatant references
        sa.Column('guardian_id', sa.String(length=150), nullable=False),
        sa.Column('adversarial_id', sa.String(length=150), nullable=False),
        sa.Column('guardian_level', sa.Integer(), nullable=False),
        sa.Column('adversarial_level', sa.Integer(), nullable=False),
        sa.Column('guardian_name', sa.String(length=100), nullable=False),
        sa.Column('adversarial_name', sa.String(length=100), nullable=False),
        # Outcome
        sa.Column('outcome', sa.String(length=30), nullable=False),
        sa.Column('total_turns', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_guesses', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('secret_leaked_at_round', sa.Integer(), nullable=True),
        sa.Column('secret_guessed_at_attempt', sa.Integer(), nullable=True),
        # ELO changes
        sa.Column('guardian_elo_before', sa.Float(), nullable=True),
        sa.Column('guardian_elo_after', sa.Float(), nullable=True),
        sa.Column('adversarial_elo_before', sa.Float(), nullable=True),
        sa.Column('adversarial_elo_after', sa.Float(), nullable=True),
        # Config snapshot
        sa.Column('max_turns', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('max_guesses', sa.Integer(), nullable=True, server_default='3'),
        # Detailed data stored as JSON text
        sa.Column('rounds_json', sa.Text(), nullable=True),
        sa.Column('guesses_json', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_arena_battles_battle_id'),
        'arena_battles',
        ['battle_id'],
        unique=True,
    )
    op.create_index(
        op.f('ix_arena_battles_guardian_id'),
        'arena_battles',
        ['guardian_id'],
    )
    op.create_index(
        op.f('ix_arena_battles_adversarial_id'),
        'arena_battles',
        ['adversarial_id'],
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_arena_battles_adversarial_id'), table_name='arena_battles')
    op.drop_index(op.f('ix_arena_battles_guardian_id'), table_name='arena_battles')
    op.drop_index(op.f('ix_arena_battles_battle_id'), table_name='arena_battles')
    op.drop_table('arena_battles')
    op.drop_index(op.f('ix_arena_combatants_combatant_id'), table_name='arena_combatants')
    op.drop_table('arena_combatants')
