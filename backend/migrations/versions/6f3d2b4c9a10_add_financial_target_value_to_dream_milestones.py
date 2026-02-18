"""add financial target value to dream milestones

Revision ID: 6f3d2b4c9a10
Revises: 5a11c6d90b22
Create Date: 2026-02-18 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6f3d2b4c9a10"
down_revision: Union[str, None] = "5a11c6d90b22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dream_milestones",
        sa.Column("financial_target_value", sa.Numeric(14, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dream_milestones", "financial_target_value")
