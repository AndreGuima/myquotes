"""add reading list tables

Revision ID: c24e5a1bd7f1
Revises: b1d6c3e9a2f4
Create Date: 2026-02-03 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c24e5a1bd7f1"
down_revision: Union[str, None] = "b1d6c3e9a2f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reading_list_books",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("author", sa.String(length=150), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="to_read"
        ),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_reading_list_books_user_id",
        "reading_list_books",
        ["user_id"],
    )
    op.create_index(
        "ix_reading_list_books_status",
        "reading_list_books",
        ["status"],
    )

    op.create_table(
        "reading_list_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["book_id"], ["reading_list_books.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("book_id", "log_date", name="uq_reading_log_book_date"),
    )
    op.create_index(
        "ix_reading_list_logs_book_id",
        "reading_list_logs",
        ["book_id"],
    )
    op.create_index(
        "ix_reading_list_logs_log_date",
        "reading_list_logs",
        ["log_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_reading_list_logs_log_date", table_name="reading_list_logs")
    op.drop_index("ix_reading_list_logs_book_id", table_name="reading_list_logs")
    op.drop_table("reading_list_logs")
    op.drop_index("ix_reading_list_books_status", table_name="reading_list_books")
    op.drop_index("ix_reading_list_books_user_id", table_name="reading_list_books")
    op.drop_table("reading_list_books")
