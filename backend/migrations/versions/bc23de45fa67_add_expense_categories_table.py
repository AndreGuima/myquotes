"""add expense categories table

Revision ID: bc23de45fa67
Revises: ab12cd34ef56
Create Date: 2026-02-20 00:00:01.000000
"""

from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc23de45fa67"
down_revision: Union[str, None] = "ab12cd34ef56"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "expense_categories",
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
    op.create_index(
        "ix_expense_categories_user_id",
        "expense_categories",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_expense_categories_user_id", table_name="expense_categories")
    op.drop_table("expense_categories")
