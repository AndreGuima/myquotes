"""add description to habits

Revision ID: 2e8f4a1b7c3d
Revises: ef56ab78cd90
Create Date: 2026-02-27 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e8f4a1b7c3d"
down_revision: Union[str, None] = "ef56ab78cd90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("habits", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("habits", "description")
