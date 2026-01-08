"""add habits table

Revision ID: 4b9c77647bd2
Revises: 959bc27889cc
Create Date: 2026-01-08 09:26:11.509247

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4b9c77647bd2"
down_revision: Union[str, None] = "959bc27889cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enum para frequência do hábito
    frequency_enum = sa.Enum(
        "daily",
        "weekly",
        name="frequency_type_enum",
    )

    # Cria enum explicitamente (MySQL safe)
    frequency_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "habits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "frequency_type",
            frequency_enum,
            nullable=False,
            server_default="daily",
        ),
        sa.Column("target_per_week", sa.Integer(), nullable=True),
        sa.Column(
            "is_active",
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
    )

    # Índice para consultas por usuário
    op.create_index(
        "ix_habits_user_id",
        "habits",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_habits_user_id", table_name="habits")
    op.drop_table("habits")

    frequency_enum = sa.Enum(
        "daily",
        "weekly",
        name="frequency_type_enum",
    )
    frequency_enum.drop(op.get_bind(), checkfirst=True)
