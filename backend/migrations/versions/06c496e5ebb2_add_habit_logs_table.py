"""add habit logs table

Revision ID: 06c496e5ebb2
Revises: 4b9c77647bd2
Create Date: 2026-01-08 12:08:24.663851
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "06c496e5ebb2"
down_revision: Union[str, None] = "4b9c77647bd2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "habit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "habit_id",
            sa.Integer(),
            sa.ForeignKey("habits.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "habit_id",
            "date",
            name="uq_habit_logs_habit_date",
        ),
    )

    op.create_index(
        "ix_habit_logs_user_date",
        "habit_logs",
        ["user_id", "date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_habit_logs_user_date",
        table_name="habit_logs",
    )
    op.drop_table("habit_logs")
