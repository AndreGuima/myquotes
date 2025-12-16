"""add receive_daily_quote to users

Revision ID: 3dea5308f206
Revises: ad365183391a
Create Date: 2025-12-15 15:58:40.917646
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "3dea5308f206"
down_revision: Union[str, None] = "ad365183391a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1️⃣ Adiciona a coluna permitindo NULL temporariamente
    op.add_column(
        "users",
        sa.Column(
            "receive_daily_quote",
            sa.Boolean(),
            nullable=True,
        ),
    )

    # 2️⃣ Backfill para usuários existentes
    op.execute(
        text(
            """
            UPDATE users
            SET receive_daily_quote = TRUE
            WHERE receive_daily_quote IS NULL
            """
        )
    )

    # 3️⃣ Torna a coluna NOT NULL
    op.alter_column(
        "users",
        "receive_daily_quote",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("users", "receive_daily_quote")
