import sqlalchemy as sa
from alembic import op

# 🚨 Ajuste EXATO conforme sua última migration
revision = "add_is_active_field"
down_revision = "add_email_verification"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
    )


def downgrade():
    op.drop_column("users", "is_active")

