"""add bank accounts table

Revision ID: 2c9a7f6e8b11
Revises: d1b7c4a9f321
Create Date: 2026-02-18 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2c9a7f6e8b11"
down_revision: Union[str, None] = "d1b7c4a9f321"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("objective_dream_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("total_value", sa.Numeric(14, 2), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["objective_dream_id"], ["dreams.id"], ondelete="RESTRICT"
        ),
    )
    op.create_index("ix_bank_accounts_user_id", "bank_accounts", ["user_id"])
    op.create_index(
        "ix_bank_accounts_objective_dream_id",
        "bank_accounts",
        ["objective_dream_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_bank_accounts_objective_dream_id",
        table_name="bank_accounts",
    )
    op.drop_index("ix_bank_accounts_user_id", table_name="bank_accounts")
    op.drop_table("bank_accounts")
