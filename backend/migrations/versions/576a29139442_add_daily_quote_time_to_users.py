"""add daily quote time to users

Revision ID: 576a29139442
Revises: 3dea5308f206
Create Date: 2025-12-15 17:45:18.618834

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "576a29139442"
down_revision: Union[str, None] = "3dea5308f206"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1️⃣ Adiciona coluna permitindo NULL temporariamente
    op.add_column(
        "users",
        sa.Column("daily_quote_time", sa.Time(), nullable=True),
    )

    # 2️⃣ Backfill para usuários existentes
    op.execute(
        text(
            """
            UPDATE users
            SET daily_quote_time = '08:00:00'
            WHERE daily_quote_time IS NULL
            """
        )
    )

    # 3️⃣ Torna NOT NULL
    op.alter_column(
        "users",
        "daily_quote_time",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("users", "daily_quote_time")
