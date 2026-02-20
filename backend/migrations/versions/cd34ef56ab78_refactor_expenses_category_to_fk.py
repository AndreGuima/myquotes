"""refactor expenses category string to foreign key

Revision ID: cd34ef56ab78
Revises: bc23de45fa67
Create Date: 2026-02-20 00:00:02.000000
"""

from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cd34ef56ab78"
down_revision: Union[str, None] = "bc23de45fa67"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ux_expense_categories_user_name",
        "expense_categories",
        ["user_id", "name"],
        unique=True,
    )

    op.add_column(
        "expenses",
        sa.Column("expense_category_id", sa.Integer(), nullable=True),
    )

    op.create_index(
        "ix_expenses_expense_category_id",
        "expenses",
        ["expense_category_id"],
    )

    op.create_foreign_key(
        "fk_expenses_expense_category_id",
        "expenses",
        "expense_categories",
        ["expense_category_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    # Cria categorias únicas por usuário com base no texto existente.
    op.execute(
        """
        INSERT INTO expense_categories (user_id, name)
        SELECT DISTINCT e.user_id,
            COALESCE(NULLIF(TRIM(e.category), ''), 'Sem categoria') AS normalized_name
        FROM expenses e
        WHERE NOT EXISTS (
            SELECT 1
            FROM expense_categories ec
            WHERE ec.user_id = e.user_id
              AND ec.name = COALESCE(NULLIF(TRIM(e.category), ''), 'Sem categoria')
        )
        """
    )

    # Vincula despesas à categoria normalizada.
    op.execute(
        """
        UPDATE expenses e
        JOIN expense_categories ec
          ON ec.user_id = e.user_id
         AND ec.name = COALESCE(NULLIF(TRIM(e.category), ''), 'Sem categoria')
        SET e.expense_category_id = ec.id
        WHERE e.expense_category_id IS NULL
        """
    )

    op.alter_column(
        "expenses",
        "expense_category_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_column("expenses", "category")


def downgrade() -> None:
    op.add_column(
        "expenses",
        sa.Column("category", sa.String(length=120), nullable=True),
    )

    op.execute(
        """
        UPDATE expenses e
        LEFT JOIN expense_categories ec ON ec.id = e.expense_category_id
        SET e.category = COALESCE(ec.name, 'Sem categoria')
        """
    )

    op.alter_column(
        "expenses",
        "category",
        existing_type=sa.String(length=120),
        nullable=False,
    )

    op.drop_constraint(
        "fk_expenses_expense_category_id",
        "expenses",
        type_="foreignkey",
    )
    op.drop_index("ix_expenses_expense_category_id", table_name="expenses")
    op.drop_column("expenses", "expense_category_id")
    op.drop_index("ux_expense_categories_user_name", table_name="expense_categories")
