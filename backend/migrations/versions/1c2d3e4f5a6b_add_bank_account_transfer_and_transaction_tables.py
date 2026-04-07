"""add bank account transfer and transaction tables

Revision ID: 1c2d3e4f5a6b
Revises: aa91c5e7d204, fe6de03c9a91, 7a20bee1e795, 00a78ad4951e
Create Date: 2026-03-20 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1c2d3e4f5a6b"
down_revision: Union[str, None] = (
    "aa91c5e7d204",
    "fe6de03c9a91",
    "7a20bee1e795",
    "00a78ad4951e",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("route_key", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ux_idempotency_keys_user_route_key",
        "idempotency_keys",
        ["user_id", "route_key", "idempotency_key"],
        unique=True,
    )

    op.create_table(
        "bank_account_transfers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("from_account_id", sa.Integer(), nullable=False),
        sa.Column("to_account_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["from_account_id"], ["bank_accounts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["to_account_id"], ["bank_accounts.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_bank_account_transfers_user_id", "bank_account_transfers", ["user_id"]
    )
    op.create_index(
        "ix_bank_account_transfers_from_account_id",
        "bank_account_transfers",
        ["from_account_id"],
    )
    op.create_index(
        "ix_bank_account_transfers_to_account_id",
        "bank_account_transfers",
        ["to_account_id"],
    )

    op.create_table(
        "bank_account_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum(
                "opening_balance",
                "manual_adjustment",
                "transfer",
                "expense",
                "expense_adjustment",
                "expense_reversal",
                "invoice_payment",
                "investment_income",
                "investment_income_adjustment",
                "investment_income_reversal",
                name="bank_account_transaction_type",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["account_id"], ["bank_accounts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["transfer_id"], ["bank_account_transfers.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "idx_bat_user_id",
        "bank_account_transactions",
        ["user_id"],
    )
    op.create_index(
        "idx_bat_account_id",
        "bank_account_transactions",
        ["account_id"],
    )
    op.create_index(
        "idx_bat_transfer_id",
        "bank_account_transactions",
        ["transfer_id"],
    )
    op.create_index(
        "idx_bat_created_at",
        "bank_account_transactions",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ux_idempotency_keys_user_route_key",
        table_name="idempotency_keys",
    )
    op.drop_table("idempotency_keys")

    op.drop_index(
        "idx_bat_created_at",
        table_name="bank_account_transactions",
    )
    op.drop_index(
        "idx_bat_transfer_id",
        table_name="bank_account_transactions",
    )
    op.drop_index(
        "idx_bat_account_id",
        table_name="bank_account_transactions",
    )
    op.drop_index(
        "idx_bat_user_id",
        table_name="bank_account_transactions",
    )
    op.drop_table("bank_account_transactions")

    op.drop_index(
        "ix_bank_account_transfers_to_account_id",
        table_name="bank_account_transfers",
    )
    op.drop_index(
        "ix_bank_account_transfers_from_account_id",
        table_name="bank_account_transfers",
    )
    op.drop_index(
        "ix_bank_account_transfers_user_id",
        table_name="bank_account_transfers",
    )
    op.drop_table("bank_account_transfers")
