"""Add user roles, approval status, and activity logging

Revision ID: 003_user_roles
Revises: 002_arena_tables
Create Date: 2026-02-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import bcrypt
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '003_user_roles'
down_revision: Union[str, None] = '002_arena_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add role column with default 'user'
    op.add_column(
        'users',
        sa.Column('role', sa.String(length=20), nullable=False, server_default='user')
    )
    # Add is_approved column with default False
    op.add_column(
        'users',
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )

    # Mark all existing users as approved so they are not locked out
    op.execute("UPDATE users SET is_approved = true")

    # Create user_activity table for logging
    op.create_table(
        'user_activity',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_activity_user_id', 'user_activity', ['user_id'])
    op.create_index('ix_user_activity_timestamp', 'user_activity', ['timestamp'])

    # Seed a default admin user
    users_table = sa.table(
        'users',
        sa.column('username', sa.String),
        sa.column('email', sa.String),
        sa.column('hashed_password', sa.String),
        sa.column('role', sa.String),
        sa.column('is_approved', sa.Boolean),
        sa.column('created_at', sa.DateTime),
    )
    hashed_pw = bcrypt.hashpw(
        'L3kf3xYfpyBikSqg'.encode('utf-8'),
        bcrypt.gensalt(),
    ).decode('utf-8')
    op.execute(
        users_table.insert().values(
            username='admin',
            email=None,
            hashed_password=hashed_pw,
            role='admin',
            is_approved=True,
            created_at=datetime.utcnow(),
        )
    )


def downgrade() -> None:
    # Remove seeded admin
    op.execute("DELETE FROM users WHERE username = 'admin' AND role = 'admin'")
    op.drop_index('ix_user_activity_timestamp', table_name='user_activity')
    op.drop_index('ix_user_activity_user_id', table_name='user_activity')
    op.drop_table('user_activity')
    op.drop_column('users', 'is_approved')
    op.drop_column('users', 'role')
