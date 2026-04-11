"""Google OAuth, email verification, and auto-approve

Revision ID: 005
Revises: 004
Create Date: 2026-04-08

Adds:
- auth_provider column (local/google)
- google_id column (for Google OAuth users)
- email_verified column
- email_verification_token column
- email_verification_expires column
- Changes is_approved default to true
- Makes hashed_password nullable (Google OAuth users have no password)
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "005_google_oauth_email"
down_revision = "004_arena_validation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add auth_provider column
    op.add_column(
        "users",
        sa.Column("auth_provider", sa.String(20), nullable=False, server_default="local"),
    )

    # Add google_id column with unique constraint
    op.add_column(
        "users",
        sa.Column("google_id", sa.String(255), nullable=True),
    )
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)

    # Add email verification columns
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_token", sa.String(255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_expires", sa.DateTime(), nullable=True),
    )

    # Make hashed_password nullable (Google OAuth users don't have a password)
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(255),
        nullable=True,
    )

    # Change is_approved default to true (auto-approve on registration)
    op.alter_column(
        "users",
        "is_approved",
        server_default="true",
    )

    # Mark all existing approved users as email_verified (they were approved before this feature)
    op.execute("UPDATE users SET email_verified = true WHERE is_approved = true")
    # Mark all existing users as auth_provider = 'local'
    op.execute("UPDATE users SET auth_provider = 'local' WHERE auth_provider IS NULL")


def downgrade() -> None:
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "email_verification_expires")
    op.drop_column("users", "email_verification_token")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "google_id")
    op.drop_column("users", "auth_provider")

    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(255),
        nullable=False,
    )

    op.alter_column(
        "users",
        "is_approved",
        server_default="false",
    )
