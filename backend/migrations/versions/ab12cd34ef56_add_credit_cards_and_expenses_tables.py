"""add credit cards and expenses tables

Revision ID: ab12cd34ef56
Revises: 8c1d4e7f9a20
Create Date: 2026-02-20 00:00:00.000000
"""

from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ab12cd34ef56"
down_revision: Union[str, None] = "8c1d4e7f9a20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "credit_cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_credit_cards_user_id", "credit_cards", ["user_id"])

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Numeric(14, 2), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("payment_method", sa.String(length=10), nullable=False),
        sa.Column("bank_account_id", sa.Integer(), nullable=True),
        sa.Column("credit_card_id", sa.Integer(), nullable=True),
        sa.Column("launch_date", sa.Date(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["credit_card_id"], ["credit_cards.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_expenses_user_id", "expenses", ["user_id"])
    op.create_index("ix_expenses_launch_date", "expenses", ["launch_date"])


def downgrade() -> None:
    op.drop_index("ix_expenses_launch_date", table_name="expenses")
    op.drop_index("ix_expenses_user_id", table_name="expenses")
    op.drop_table("expenses")

    op.drop_index("ix_credit_cards_user_id", table_name="credit_cards")
    op.drop_table("credit_cards")
