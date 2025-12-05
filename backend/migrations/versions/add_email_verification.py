import sqlalchemy as sa
from alembic import op

revision = "add_email_verification"
down_revision = "add_auto_admin_user"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), server_default="0", nullable=False),
    )


def downgrade():
    op.drop_column("users", "is_verified")
