"""add patrimony snapshot accounts table

Revision ID: f17c9a0d4b21
Revises: 148b24823bf6
Create Date: 2026-03-13 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f17c9a0d4b21"
down_revision: Union[str, None] = "148b24823bf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "patrimony_snapshots",
        sa.Column(
            "has_breakdown",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.alter_column("patrimony_snapshots", "has_breakdown", server_default=None)

    op.create_table(
        "patrimony_snapshot_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("snapshot_id", sa.Integer(), nullable=False),
        sa.Column("bank_account_id", sa.Integer(), nullable=True),
        sa.Column("account_name", sa.String(length=120), nullable=False),
        sa.Column("total_value", sa.Numeric(14, 2), nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"], ["patrimony_snapshots.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_patrimony_snapshot_accounts_snapshot_id",
        "patrimony_snapshot_accounts",
        ["snapshot_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_patrimony_snapshot_accounts_snapshot_id",
        table_name="patrimony_snapshot_accounts",
    )
    op.drop_table("patrimony_snapshot_accounts")
    op.drop_column("patrimony_snapshots", "has_breakdown")
