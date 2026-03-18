"""add investments and price history tables

Revision ID: f2c4b7a1d9e0
Revises: 148b24823bf6
Create Date: 2026-03-17 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2c4b7a1d9e0"
down_revision: Union[str, None] = "148b24823bf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "investments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "asset_type",
            sa.Enum("stock", "fii", name="investment_asset_type_enum"),
            nullable=False,
        ),
        sa.Column("sector", sa.String(length=120), server_default="", nullable=False),
        sa.Column("ticker", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("average_price", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("current_price", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("price_updated_at", sa.DateTime(), nullable=True),
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
    op.create_index(
        "ix_investments_user_asset_type", "investments", ["user_id", "asset_type"]
    )
    op.create_index("ix_investments_user_ticker", "investments", ["user_id", "ticker"])

    op.create_table(
        "investment_price_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("investment_id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=30), nullable=False),
        sa.Column("price", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column(
            "currency", sa.String(length=10), server_default="BRL", nullable=False
        ),
        sa.Column(
            "source", sa.String(length=30), server_default="brapi", nullable=False
        ),
        sa.Column(
            "captured_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["investment_id"], ["investments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_investment_price_history_investment_captured_at",
        "investment_price_history",
        ["investment_id", "captured_at"],
    )
    op.create_index(
        "ix_investment_price_history_user_ticker_captured_at",
        "investment_price_history",
        ["user_id", "ticker", "captured_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_investment_price_history_user_ticker_captured_at",
        table_name="investment_price_history",
    )
    op.drop_index(
        "ix_investment_price_history_investment_captured_at",
        table_name="investment_price_history",
    )
    op.drop_table("investment_price_history")
    op.drop_index("ix_investments_user_ticker", table_name="investments")
    op.drop_index("ix_investments_user_asset_type", table_name="investments")
    op.drop_table("investments")
