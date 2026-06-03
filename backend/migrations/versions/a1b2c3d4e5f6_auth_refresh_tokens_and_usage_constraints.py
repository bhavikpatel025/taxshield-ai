"""auth refresh tokens and usage constraints

Revision ID: a1b2c3d4e5f6
Revises: 979461f75dc1
Create Date: 2026-06-03 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "979461f75dc1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "failed_login_attempts",
        existing_type=sa.String(length=10),
        type_=sa.Integer(),
        existing_nullable=True,
        nullable=False,
        server_default="0",
        postgresql_using="failed_login_attempts::integer",
    )
    op.alter_column("users", "failed_login_attempts", server_default=None)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_token_hash"), "refresh_tokens", ["token_hash"], unique=True)

    op.create_unique_constraint("uq_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_unique_constraint(
        "uq_usage_tracking_user_type_date",
        "usage_tracking",
        ["user_id", "usage_type", "usage_date"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_usage_tracking_user_type_date", "usage_tracking", type_="unique")
    op.drop_constraint("uq_subscriptions_user_id", "subscriptions", type_="unique")
    op.drop_index(op.f("ix_refresh_tokens_token_hash"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.alter_column(
        "users",
        "failed_login_attempts",
        existing_type=sa.Integer(),
        type_=sa.String(length=10),
        existing_nullable=False,
        nullable=True,
        postgresql_using="failed_login_attempts::text",
    )
