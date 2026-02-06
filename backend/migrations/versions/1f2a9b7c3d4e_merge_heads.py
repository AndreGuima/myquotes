"""merge heads after habit time range

Revision ID: 1f2a9b7c3d4e
Revises: b6c1f8a1b7c2, c24e5a1bd7f1
Create Date: 2026-02-04 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f2a9b7c3d4e"
down_revision: Union[str, None] = ("b6c1f8a1b7c2", "c24e5a1bd7f1")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
