"""remove smart fields from dreams

Revision ID: c5f1d8a2b9e3
Revises: aa91c5e7d204, 0f6a7b8c9d10
Create Date: 2026-08-18 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5f1d8a2b9e3"
down_revision: Union[str, None] = ("aa91c5e7d204", "0f6a7b8c9d10")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("dreams", "smart_specific")
    op.drop_column("dreams", "smart_measurable")
    op.drop_column("dreams", "smart_achievable")
    op.drop_column("dreams", "smart_relevant")
    op.drop_column("dreams", "smart_time_bound")


def downgrade() -> None:
    op.add_column(
        "dreams",
        sa.Column("smart_specific", sa.Text(), nullable=True),
    )
    op.add_column(
        "dreams",
        sa.Column("smart_measurable", sa.Text(), nullable=True),
    )
    op.add_column(
        "dreams",
        sa.Column("smart_achievable", sa.Text(), nullable=True),
    )
    op.add_column(
        "dreams",
        sa.Column("smart_relevant", sa.Text(), nullable=True),
    )
    op.add_column(
        "dreams",
        sa.Column("smart_time_bound", sa.Text(), nullable=True),
    )
