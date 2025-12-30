"""remove quote preferences from users

Revision ID: 52a683a7bca0
Revises: 7a20bee1e795
Create Date: 2025-12-30 11:10:03.405339
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "52a683a7bca0"
down_revision = "7a20bee1e795"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 🔐 batch_alter_table garante compatibilidade com SQLite (pytest)
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("receive_daily_quote")
        batch_op.drop_column("daily_quote_time")


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "receive_daily_quote",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "daily_quote_time",
                sa.Time(),
                nullable=True,
            )
        )
