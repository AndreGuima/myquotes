"""add patrimony snapshots table

Revision ID: 8c1d4e7f9a20
Revises: 6f3d2b4c9a10
Create Date: 2026-02-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8c1d4e7f9a20"
down_revision: Union[str, None] = "6f3d2b4c9a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "patrimony_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total_value", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "snapshot_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_patrimony_snapshots_user_id",
        "patrimony_snapshots",
        ["user_id"],
    )
    op.create_index(
        "ix_patrimony_snapshots_snapshot_at",
        "patrimony_snapshots",
        ["snapshot_at"],
    )

    # Backfill inicial: um snapshot por usuário com total atual em contas.
    op.execute(
        """
        INSERT INTO patrimony_snapshots (user_id, total_value, snapshot_at)
        SELECT ba.user_id, COALESCE(SUM(ba.total_value), 0), CURRENT_TIMESTAMP
        FROM bank_accounts ba
        GROUP BY ba.user_id
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_patrimony_snapshots_snapshot_at", table_name="patrimony_snapshots"
    )
    op.drop_index("ix_patrimony_snapshots_user_id", table_name="patrimony_snapshots")
    op.drop_table("patrimony_snapshots")
