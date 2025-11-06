from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_ENV: str = Field("development")
    APP_HOST: str = Field("0.0.0.0")
    APP_PORT: int = Field(8000)

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_NAME: str

    class Config:
        env_file = ".env"
        extra = "allow"  # ✅ aceita variáveis extras sem erro

settings = Settings()
