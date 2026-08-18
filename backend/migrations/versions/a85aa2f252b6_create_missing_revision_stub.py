"""stub migration to restore missing revision a85aa2f252b6

Revision ID: a85aa2f252b6
Revises: add_is_active_field
Create Date: 2026-08-14 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a85aa2f252b6"
down_revision: Union[str, None] = "add_is_active_field"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a stub migration created to restore a missing revision
    # The schema changes are assumed already present in the database.
    # No operations here to avoid duplicating changes.
    pass


def downgrade() -> None:
    # No-op
    pass
