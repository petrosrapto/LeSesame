"""Add validation columns to arena_combatants

Revision ID: 004_arena_validation
Revises: 003_user_roles
Create Date: 2026-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_arena_validation'
down_revision: Union[str, None] = '003_user_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'arena_combatants',
        sa.Column('validated', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )
    op.add_column(
        'arena_combatants',
        sa.Column('validation_passed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )
    op.add_column(
        'arena_combatants',
        sa.Column('validated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('arena_combatants', 'validated_at')
    op.drop_column('arena_combatants', 'validation_passed')
    op.drop_column('arena_combatants', 'validated')
