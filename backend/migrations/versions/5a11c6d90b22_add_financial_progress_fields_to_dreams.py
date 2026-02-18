"""add financial progress fields to dreams

Revision ID: 5a11c6d90b22
Revises: 2c9a7f6e8b11
Create Date: 2026-02-18 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5a11c6d90b22"
down_revision: Union[str, None] = "2c9a7f6e8b11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dreams",
        sa.Column("smart_financial_target_value", sa.Numeric(14, 2), nullable=True),
    )

    op.add_column(
        "dream_milestones",
        sa.Column(
            "progress_percent",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("dream_milestones", "progress_percent")
    op.drop_column("dreams", "smart_financial_target_value")
