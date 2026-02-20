"""add composite indexes for expenses queries

Revision ID: ef56ab78cd90
Revises: de45fa67bc89
Create Date: 2026-02-20 00:00:04.000000
"""

from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ef56ab78cd90"
down_revision: Union[str, None] = "de45fa67bc89"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_expenses_user_launch_date_id",
        "expenses",
        ["user_id", "launch_date", "id"],
    )
    op.create_index(
        "ix_expenses_user_expense_category_id",
        "expenses",
        ["user_id", "expense_category_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_expenses_user_expense_category_id", table_name="expenses")
    op.drop_index("ix_expenses_user_launch_date_id", table_name="expenses")
