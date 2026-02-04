"""add habit time range

Revision ID: b6c1f8a1b7c2
Revises: 4b9c77647bd2
Create Date: 2026-02-04 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b6c1f8a1b7c2"
down_revision: Union[str, None] = "4b9c77647bd2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("habits", sa.Column("start_time", sa.Time(), nullable=True))
    op.add_column("habits", sa.Column("end_time", sa.Time(), nullable=True))


def downgrade() -> None:
    op.drop_column("habits", "end_time")
    op.drop_column("habits", "start_time")
