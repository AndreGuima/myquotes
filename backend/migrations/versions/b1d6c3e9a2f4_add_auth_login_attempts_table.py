"""add auth login attempts table

Revision ID: b1d6c3e9a2f4
Revises: 06c496e5ebb2
Create Date: 2026-02-03 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1d6c3e9a2f4"
down_revision: Union[str, None] = "06c496e5ebb2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_login_attempts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_attempt_at", sa.DateTime(), nullable=True),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.UniqueConstraint(
            "email",
            "ip_address",
            name="uq_auth_login_attempts_email_ip",
        ),
    )
    op.create_index(
        "ix_auth_login_attempts_email",
        "auth_login_attempts",
        ["email"],
    )
    op.create_index(
        "ix_auth_login_attempts_ip",
        "auth_login_attempts",
        ["ip_address"],
    )


def downgrade() -> None:
    op.drop_index("ix_auth_login_attempts_ip", table_name="auth_login_attempts")
    op.drop_index("ix_auth_login_attempts_email", table_name="auth_login_attempts")
    op.drop_table("auth_login_attempts")
