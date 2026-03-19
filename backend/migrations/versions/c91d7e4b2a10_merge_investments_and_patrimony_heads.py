"""merge investments and patrimony heads

Revision ID: c91d7e4b2a10
Revises: f17c9a0d4b21, f2c4b7a1d9e0
Create Date: 2026-03-17 00:00:00.000000
"""

from typing import Sequence, Union

revision: str = "c91d7e4b2a10"
down_revision: Union[str, None] = ("f17c9a0d4b21", "f2c4b7a1d9e0")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
