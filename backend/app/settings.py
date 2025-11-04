from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()
