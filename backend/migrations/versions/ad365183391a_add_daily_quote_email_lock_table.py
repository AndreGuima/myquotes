"""add daily quote email lock table

Revision ID: ad365183391a
Revises: a85aa2f252b6
Create Date: 2025-12-14 10:01:13.183937
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ad365183391a"
down_revision: Union[str, None] = "a85aa2f252b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_quote_email_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 🔒 Lock diário: garante 1 envio por usuário por dia
    op.create_unique_constraint(
        "uq_daily_quote_email_user_date",
        "daily_quote_email_logs",
        ["user_id", "date"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_daily_quote_email_user_date",
        "daily_quote_email_logs",
        type_="unique",
    )
    op.drop_table("daily_quote_email_logs")
