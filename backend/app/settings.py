from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 🔧 Configurações gerais do app
    APP_ENV: str = Field(default="development")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # 🎯 Modo de teste
    TESTING: bool = Field(default=False)

    # 💾 Configurações do banco de dados
    DB_USER: str = Field(default="test_user")
    DB_PASSWORD: str = Field(default="test_pass")
    DB_HOST: str = Field(default="mysql")
    DB_PORT: int = Field(default=3306)
    DB_NAME: str = Field(default="test_db")

    # ✉️ Email (SMTP)
    EMAIL_ENABLED: bool = Field(default=False)
    EMAIL_FROM: str = Field(default="MyQuotes <no-reply@myquotes.dev>")

    SMTP_HOST: str = Field(default="mailhog")
    SMTP_PORT: int = Field(default=1025)
    SMTP_USER: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)

    # ⚙️ Configurações do Pydantic v2
    model_config = ConfigDict(
        env_file=".env",
        extra="allow",
    )


settings = Settings()

# --------------------------------------------------------------------
# 🔥 Ajustes automáticos para ambiente de testes
# --------------------------------------------------------------------
if settings.TESTING:
    settings.DB_USER = "test_user"
    settings.DB_PASSWORD = "test_pass"
    settings.DB_NAME = "test_db"
    settings.DB_HOST = "localhost"
    settings.DB_PORT = 3306

    # ❌ Nunca enviar email em testes
    settings.EMAIL_ENABLED = False
