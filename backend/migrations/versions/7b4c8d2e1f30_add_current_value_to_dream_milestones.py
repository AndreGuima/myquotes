"""add current value to dream milestones

Revision ID: 7b4c8d2e1f30
Revises: 6f3d2b4c9a10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "7b4c8d2e1f30"
down_revision: Union[str, None] = "6f3d2b4c9a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dream_milestones",
        sa.Column("financial_current_value", sa.Numeric(14, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dream_milestones", "financial_current_value")
