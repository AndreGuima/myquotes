"""merge alembic branches

Revision ID: fe6de03c9a91
Revises: 52a683a7bca0, dd5a4f1f07b4
Create Date: 2026-01-02 16:08:57.083897

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fe6de03c9a91"
down_revision: Union[str, None] = ("52a683a7bca0", "dd5a4f1f07b4")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
