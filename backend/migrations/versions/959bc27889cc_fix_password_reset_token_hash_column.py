"""fix password reset token hash column

Revision ID: 959bc27889cc
Revises: fe6de03c9a91
Create Date: 2026-01-03 12:12:31.545918
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "959bc27889cc"
down_revision = "fe6de03c9a91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("password_reset_tokens") as batch_op:
        # 1️⃣ Renomeia coluna token -> token_hash (sem perder dados)
        batch_op.alter_column(
            "token",
            new_column_name="token_hash",
            existing_type=sa.String(length=255),
        )

        # 2️⃣ Remove constraint antiga (se existir)
        batch_op.drop_constraint(
            "uq_password_reset_tokens_token",
            type_="unique",
        )

        # 3️⃣ Cria índice único correto
        batch_op.create_index(
            "ix_password_reset_token_hash",
            ["token_hash"],
            unique=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("password_reset_tokens") as batch_op:
        # rollback limpo e seguro
        batch_op.drop_index("ix_password_reset_token_hash")

        batch_op.alter_column(
            "token_hash",
            new_column_name="token",
            existing_type=sa.String(length=255),
        )

        batch_op.create_unique_constraint(
            "uq_password_reset_tokens_token",
            ["token"],
        )
