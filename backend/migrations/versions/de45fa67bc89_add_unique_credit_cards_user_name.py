"""add unique credit cards user name

Revision ID: de45fa67bc89
Revises: cd34ef56ab78
Create Date: 2026-02-20 00:00:03.000000
"""

from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "de45fa67bc89"
down_revision: Union[str, None] = "cd34ef56ab78"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Deduplica cartões por (user_id, name), preservando o menor id.
    # Primeiro reatribui despesas para o cartão canônico.
    op.execute(
        """
        UPDATE expenses e
        JOIN credit_cards cc_dup ON cc_dup.id = e.credit_card_id
        JOIN (
            SELECT user_id, name, MIN(id) AS keep_id
            FROM credit_cards
            GROUP BY user_id, name
            HAVING COUNT(*) > 1
        ) dups
          ON dups.user_id = cc_dup.user_id
         AND dups.name = cc_dup.name
        SET e.credit_card_id = dups.keep_id
        WHERE e.credit_card_id <> dups.keep_id
        """
    )

    # Remove cartões duplicados restantes.
    op.execute(
        """
        DELETE cc
        FROM credit_cards cc
        JOIN (
            SELECT user_id, name, MIN(id) AS keep_id
            FROM credit_cards
            GROUP BY user_id, name
            HAVING COUNT(*) > 1
        ) dups
          ON dups.user_id = cc.user_id
         AND dups.name = cc.name
        WHERE cc.id <> dups.keep_id
        """
    )

    op.create_index(
        "ux_credit_cards_user_name",
        "credit_cards",
        ["user_id", "name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ux_credit_cards_user_name", table_name="credit_cards")
