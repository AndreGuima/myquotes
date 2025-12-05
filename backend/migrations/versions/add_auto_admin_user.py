import sqlalchemy as sa
from alembic import op
from passlib.context import CryptContext

# Identificadores da migration
revision = "add_auto_admin_user"
down_revision = "00a78ad4951e"
branch_labels = None
depends_on = None

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade():
    password_hash = pwd.hash("admin123")

    op.execute(
        f"""
        INSERT INTO users (username, email, password_hash, role)
        VALUES ('admin', 'admin@myquotes.dev', '{password_hash}', 'admin')
    """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM users WHERE email = 'admin@myquotes.dev';
    """
    )
