from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # DB
    DB_HOST: str = "db"
    DB_PORT: int = 3306
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Email (SMTP REAL — sempre)
    EMAIL_FROM: str | None = None

    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False

    class Config:
        extra = "allow"


settings = Settings()
