"""add habit weekdays

Revision ID: e3d91c4a77aa
Revises: 1f2a9b7c3d4e
Create Date: 2026-02-08 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e3d91c4a77aa"
down_revision: Union[str, None] = "1f2a9b7c3d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("habits", sa.Column("weekdays", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("habits", "weekdays")
