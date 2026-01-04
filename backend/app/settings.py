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

    # ✅ Pydantic v2 way
    model_config = ConfigDict(extra="allow")


# =========================
# 🔥 PONTO-CHAVE
# =========================
if os.getenv("TESTING") == "1":
    settings = Settings(
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_password",
    )
else:
    settings = Settings()
