import os
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 🔧 Configurações gerais do app
    APP_ENV: str = Field(default="development")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    TESTING: bool = Field(default=False)

    # 💾 Configurações do banco de dados
    DB_USER: str = Field(default="test_user")
    DB_PASSWORD: str = Field(default="test_pass")
    DB_HOST: str = Field(default="mysql")
    DB_PORT: int = Field(default=3306)
    DB_NAME: str = Field(default="test_db")

    # ⚙️ Configuração moderna do Pydantic v2
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
