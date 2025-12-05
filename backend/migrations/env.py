import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# -----------------------------------------------------
# 1. Load .env from project root
# -----------------------------------------------------
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

# -----------------------------------------------------
# 2. Load Alembic config
# -----------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -----------------------------------------------------
# 3. Build DATABASE_URL manually (no Settings dependency!)
# -----------------------------------------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

database_url = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?ssl_disabled=true"
)


config.set_main_option("sqlalchemy.url", database_url)

# -----------------------------------------------------
# 4. Load metadata without importing Settings()
# -----------------------------------------------------
from app.database import Base
from app.models.quote import Quote

# Importar modelos é essencial para o Alembic enxergar as tabelas!
from app.models.user import User

target_metadata = Base.metadata


# -----------------------------------------------------
# 5. Offline migration
# -----------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# -----------------------------------------------------
# 6. Online migration
# -----------------------------------------------------
def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# -----------------------------------------------------
# 7. Run
# -----------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
