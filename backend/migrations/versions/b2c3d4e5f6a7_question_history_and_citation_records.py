"""question history and citation records

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-03 18:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "question_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("question_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.Enum("ANSWERED", "UNSUPPORTED", "FAILED", name="questionstatus"), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("retrieved_chunk_count", sa.Integer(), nullable=False),
        sa.Column("unsupported_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_question_history_user_id"), "question_history", ["user_id"], unique=False)
    op.create_index(op.f("ix_question_history_question_hash"), "question_history", ["question_hash"], unique=False)

    op.create_table(
        "citation_records",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=False),
        sa.Column("source_title", sa.String(length=255), nullable=False),
        sa.Column("section", sa.String(length=100), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("validated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["question_history.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_citation_records_question_id"), "citation_records", ["question_id"], unique=False)
    op.alter_column("citation_records", "validated", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_citation_records_question_id"), table_name="citation_records")
    op.drop_table("citation_records")
    op.drop_index(op.f("ix_question_history_question_hash"), table_name="question_history")
    op.drop_index(op.f("ix_question_history_user_id"), table_name="question_history")
    op.drop_table("question_history")
    sa.Enum(name="questionstatus").drop(op.get_bind(), checkfirst=True)
