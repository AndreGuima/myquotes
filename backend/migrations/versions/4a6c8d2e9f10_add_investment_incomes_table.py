"""add investment incomes table

Revision ID: 4a6c8d2e9f10
Revises: 2e8f4a1b7c3d
Create Date: 2026-03-04 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a6c8d2e9f10"
down_revision: Union[str, None] = "2e8f4a1b7c3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "investment_incomes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("income_type", sa.String(length=30), nullable=False),
        sa.Column("ticker", sa.String(length=30), nullable=False),
        sa.Column("bank_account_id", sa.Integer(), nullable=True),
        sa.Column("received_at", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=False, server_default=""),
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
        sa.ForeignKeyConstraint(
            ["bank_account_id"], ["bank_accounts.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_investment_incomes_user_received_date_id",
        "investment_incomes",
        ["user_id", "received_at", "id"],
    )
    op.create_index(
        "ix_investment_incomes_user_bank_account_id",
        "investment_incomes",
        ["user_id", "bank_account_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_investment_incomes_user_bank_account_id",
        table_name="investment_incomes",
    )
    op.drop_index(
        "ix_investment_incomes_user_received_date_id",
        table_name="investment_incomes",
    )
    op.drop_table("investment_incomes")
