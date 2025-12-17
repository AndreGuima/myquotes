from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # =========================================================
    # 🔧 App
    # =========================================================
    APP_ENV: str = Field(default="development")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # =========================================================
    # 🧪 Testes
    # =========================================================
    TESTING: bool = Field(default=False)

    # =========================================================
    # 💾 Banco de dados
    # =========================================================
    DB_HOST: str = Field(default="db")
    DB_PORT: int = Field(default=3306)
    DB_NAME: str = Field(default="myquotes_db")
    DB_USER: str = Field(default="myquotes_user")
    DB_PASSWORD: str = Field(default="myquotes_pass")

    # =========================================================
    # ✉️ Email
    # =========================================================
    EMAIL_ENABLED: bool = Field(default=False)
    EMAIL_FROM: str = Field(default="MyQuotes <no-reply@myquotes.dev>")

    SMTP_HOST: str = Field(default="mailhog")
    SMTP_PORT: int = Field(default=1025)
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    class Config:
        extra = "allow"


settings = Settings()

# =============================================================
# 🔥 Ajustes automáticos por ambiente
# =============================================================

# 🧪 Testes
if settings.TESTING:
    settings.EMAIL_ENABLED = False

# 🚀 Produção
if settings.APP_ENV == "production":
    # aqui você pode colocar regras de produção no futuro
    pass
