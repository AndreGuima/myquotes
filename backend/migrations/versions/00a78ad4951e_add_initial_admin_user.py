"""add initial admin user

Revision ID: 00a78ad4951e
Revises: 3b7ba1276513
Create Date: 2025-11-25 20:04:16.787185

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '00a78ad4951e'
down_revision: Union[str, None] = '3b7ba1276513'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Cria usuário 'admin' com senha 'admin123'
    op.execute("""
        INSERT INTO users (username, email, password_hash, role)
        VALUES (
            'admin',
            'admin@myquotes.local',
            '$2b$12$Kc5qHXi9gYvSxrS9ODFtekR42bIvV9o2wDYp/HZoMpKxpkK7rNypC',
            'admin'
        );
    """)


def downgrade() -> None:
    # Remove o usuário admin criado na migration
    op.execute("""
        DELETE FROM users WHERE username = 'admin';
    """)
