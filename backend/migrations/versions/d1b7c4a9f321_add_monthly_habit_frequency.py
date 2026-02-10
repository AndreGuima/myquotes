"""add monthly habit frequency

Revision ID: d1b7c4a9f321
Revises: 9f4a1d2c7b10
Create Date: 2026-02-10 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1b7c4a9f321"
down_revision: Union[str, None] = "9f4a1d2c7b10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        op.execute(
            "ALTER TABLE habits "
            "MODIFY COLUMN frequency_type "
            "ENUM('daily','weekly','monthly') "
            "NOT NULL DEFAULT 'daily'"
        )
    elif dialect == "postgresql":
        op.execute("ALTER TYPE frequency_type_enum ADD VALUE IF NOT EXISTS 'monthly'")

    op.add_column("habits", sa.Column("month_day", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("habits", "month_day")

    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        op.execute(
            "ALTER TABLE habits "
            "MODIFY COLUMN frequency_type "
            "ENUM('daily','weekly') "
            "NOT NULL DEFAULT 'daily'"
        )
