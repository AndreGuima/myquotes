"""add user preferences table

Revision ID: f8e75d736a74
Revises: 576a29139442
Create Date: 2025-12-29 12:16:33
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "f8e75d736a74"
down_revision: Union[str, None] = "576a29139442"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("preferences", mysql.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_preferences_user_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            "category",
            name="uq_user_preferences_user_category",
        ),
    )

    # Índice auxiliar para consultas por usuário
    op.create_index(
        "ix_user_preferences_user_id",
        "user_preferences",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_preferences_user_id",
        table_name="user_preferences",
    )
    op.drop_table("user_preferences")
