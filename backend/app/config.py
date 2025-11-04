from sqlalchemy import create_engine
from .settings import settings

DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?ssl_disabled=true"
)

engine = create_engine(DATABASE_URL, echo=False, future=True)
