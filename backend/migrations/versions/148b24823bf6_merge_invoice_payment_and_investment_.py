"""merge invoice payment and investment income heads

Revision ID: 148b24823bf6
Revises: 7b2d9c4e1a11, a7f9c2d1e4b3
Create Date: 2026-03-10 16:16:29.506051

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "148b24823bf6"
down_revision: Union[str, None] = ("7b2d9c4e1a11", "a7f9c2d1e4b3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
