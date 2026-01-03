"""migrate receive_daily_quote to user_preferences

Revision ID: 7a20bee1e795
Revises: f8e75d736a74
Create Date: 2025-12-29 18:17:22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "7a20bee1e795"
down_revision: Union[str, None] = "f8e75d736a74"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 🛡️ Se a coluna não existe mais, a migration já foi efetivamente aplicada
    result = conn.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'users'
              AND COLUMN_NAME = 'receive_daily_quote'
            """
        )
    ).scalar()

    if result == 0:
        # Nada a fazer — banco já está no estado final
        return

    # Caso excepcional (banco muito antigo)
    conn.execute(
        sa.text(
            """
            INSERT INTO user_preferences (user_id, category, preferences)
            SELECT
                u.id,
                'notifications',
                JSON_OBJECT(
                    'daily_quote',
                    COALESCE(u.receive_daily_quote, 1)
                )
            FROM users u
            ON DUPLICATE KEY UPDATE
                preferences = JSON_SET(
                    user_preferences.preferences,
                    '$.daily_quote',
                    JSON_EXTRACT(VALUES(preferences), '$.daily_quote')
                )
            """
        )
    )


def downgrade() -> None:
    """
    Restaura users.receive_daily_quote a partir do JSON
    (rollback seguro)
    """

    conn = op.get_bind()

    conn.execute(
        text(
            """
            UPDATE users u
            JOIN user_preferences p
              ON p.user_id = u.id
             AND p.category = 'notifications'
            SET u.receive_daily_quote =
                JSON_EXTRACT(p.preferences, '$.daily_quote')
            """
        )
    )
