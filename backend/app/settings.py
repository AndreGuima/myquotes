import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # =========================
    # App
    # =========================
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # 🌐 Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # =========================
    # 🔐 Security / JWT
    # =========================
    SECRET_KEY: str

    # =========================
    # Database
    # =========================
    DB_HOST: str = "db"
    DB_PORT: int = 3306
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # =========================
    # Email
    # =========================
    EMAIL_FROM: str | None = None

    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False

    # =========================
    # 🔒 Password policy
    # =========================
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_LOWER: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # =========================
    # 🛡️ Brute-force protection
    # =========================
    BRUTE_FORCE_MAX_ATTEMPTS: int = 5
    BRUTE_FORCE_WINDOW_SECONDS: int = 900  # 15 min
    BRUTE_FORCE_LOCKOUT_SECONDS: int = 900  # 15 min

    # =========================
    # Pydantic v2
    # =========================
    model_config = ConfigDict(
        extra="allow",
        env_file=".env",
        env_file_encoding="utf-8",
    )


# =========================
# 🔥 PONTO-CHAVE
# =========================
if os.getenv("TESTING") == "1":
    # Ambiente de testes (SQLite / JWT fake)
    settings = Settings(
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_password",
        SECRET_KEY="test-secret-key",
    )
else:
    settings = Settings()
