from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    # 🔧 Configurações gerais do app
    APP_ENV: str = Field(default="development")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # 💾 Configurações do banco de dados
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = Field(default="mysql")
    DB_PORT: int = Field(default=3306)
    DB_NAME: str

    # ⚙️ Configuração moderna do Pydantic v2
    model_config = ConfigDict(
        env_file=".env",   # lê variáveis de ambiente do .env
        extra="allow"      # permite variáveis extras sem erro
    )


# ✅ Instância global de Settings
settings = Settings()
