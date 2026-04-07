"""add allow investment income to bank accounts

Revision ID: c3a9d8e1f4b2
Revises: 1c2d3e4f5a6b
Create Date: 2026-03-25 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3a9d8e1f4b2"
down_revision: Union[str, None] = "1c2d3e4f5a6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bank_accounts",
        sa.Column(
            "allow_investment_income",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("bank_accounts", "allow_investment_income")
