"""add dreams tables

Revision ID: 9f4a1d2c7b10
Revises: e3d91c4a77aa
Create Date: 2026-02-10 09:20:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f4a1d2c7b10"
down_revision: Union[str, None] = "e3d91c4a77aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dreams",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("smart_specific", sa.Text(), nullable=True),
        sa.Column("smart_measurable", sa.Text(), nullable=True),
        sa.Column("smart_achievable", sa.Text(), nullable=True),
        sa.Column("smart_relevant", sa.Text(), nullable=True),
        sa.Column("smart_time_bound", sa.Text(), nullable=True),
        sa.Column("smart_target_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dream_milestones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dream_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["dream_id"], ["dreams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dream_habit_links",
        sa.Column("dream_id", sa.Integer(), nullable=False),
        sa.Column("habit_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["dream_id"], ["dreams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["habit_id"], ["habits.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("dream_id", "habit_id"),
    )

    op.create_index("ix_dreams_user_id", "dreams", ["user_id"])
    op.create_index("ix_dream_milestones_dream_id", "dream_milestones", ["dream_id"])


def downgrade() -> None:
    op.drop_index("ix_dream_milestones_dream_id", table_name="dream_milestones")
    op.drop_index("ix_dreams_user_id", table_name="dreams")
    op.drop_table("dream_habit_links")
    op.drop_table("dream_milestones")
    op.drop_table("dreams")
