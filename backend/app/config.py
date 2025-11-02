from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER", "myquotes_user")
DB_PASS = os.getenv("DB_PASS", "myquotes_pass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "myquotes_db")

# SQLAlchemy database URL using the mysql-connector driver
DATABASE_URL = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Engine (use future=True for SQLAlchemy 1.4+/2.0 style)
engine = create_engine(DATABASE_URL, echo=False, future=True)
