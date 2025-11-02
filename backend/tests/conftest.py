import time
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

from testcontainers.mysql import MySqlContainer

# Ensure the `backend` package is importable (so `import app` works)
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from app.main import app
from app.models.quote import Base


@pytest.fixture(scope="session")
def mysql_container():
    # Start a real MySQL container for the test session.
    with MySqlContainer("mysql:8.0.33") as mysql:
        # Wait a short while for mysqld to be fully ready
        time.sleep(2)
        yield mysql


@pytest.fixture(scope="session")
def engine(mysql_container):
    # testcontainers provides a connection URL usable by SQLAlchemy
    url = mysql_container.get_connection_url()
    # force mysql+mysqlconnector scheme if needed
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+mysqlconnector://", 1)

    engine = create_engine(url, future=True)
    # create tables for testing
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_sessionmaker(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client(engine, monkeypatch):
    # Override the app module-level engine so endpoints use the test engine
    import app.main as app_main

    monkeypatch.setattr(app_main, "engine", engine)

    # Provide a TestClient that exercises the FastAPI app in-process
    with TestClient(app) as c:
        yield c
