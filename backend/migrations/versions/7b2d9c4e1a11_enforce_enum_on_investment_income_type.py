"""enforce enum on investment income type

Revision ID: 7b2d9c4e1a11
Revises: 4a6c8d2e9f10
Create Date: 2026-03-04 00:00:01.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b2d9c4e1a11"
down_revision: Union[str, None] = "4a6c8d2e9f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE investment_incomes "
        "SET income_type = 'dividend' "
        "WHERE income_type NOT IN ('dividend', 'jcp', 'rendimento')"
    )
    op.execute(
        "ALTER TABLE investment_incomes "
        "MODIFY COLUMN income_type ENUM('dividend', 'jcp', 'rendimento') NOT NULL"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE investment_incomes "
        "MODIFY COLUMN income_type VARCHAR(30) NOT NULL"
    )
