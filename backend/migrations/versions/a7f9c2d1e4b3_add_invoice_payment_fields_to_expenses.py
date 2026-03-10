"""add invoice payment fields to expenses

Revision ID: a7f9c2d1e4b3
Revises: ef56ab78cd90
Create Date: 2026-03-10 00:00:00.000000
"""

from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7f9c2d1e4b3"
down_revision: Union[str, None] = "ef56ab78cd90"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "expenses",
        sa.Column("invoice_payment_expense_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "expenses",
        sa.Column("invoice_paid_at", sa.DateTime(), nullable=True),
    )
    op.create_foreign_key(
        "fk_expenses_invoice_payment_expense_id",
        "expenses",
        "expenses",
        ["invoice_payment_expense_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_expenses_invoice_payment_expense_id",
        "expenses",
        ["invoice_payment_expense_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_expenses_invoice_payment_expense_id", table_name="expenses")
    op.drop_constraint(
        "fk_expenses_invoice_payment_expense_id",
        "expenses",
        type_="foreignkey",
    )
    op.drop_column("expenses", "invoice_paid_at")
    op.drop_column("expenses", "invoice_payment_expense_id")
