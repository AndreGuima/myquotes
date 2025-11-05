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

from app.models.quote import Base


@pytest.fixture(scope="session")
def mysql_container():
    # Start a real MySQL container for the test session.
    with MySqlContainer("mysql:8.0.33") as mysql:
        time.sleep(2)
        yield mysql


@pytest.fixture(scope="session")
def engine(mysql_container):
    url = mysql_container.get_connection_url()

    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+mysqlconnector://", 1)

    engine = create_engine(url, future=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_sessionmaker(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client(engine, monkeypatch):
    # ✅ Set fake env vars BEFORE importing app
    monkeypatch.setenv("DB_USER", "test")
    monkeypatch.setenv("DB_PASSWORD", "test")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "3306")
    monkeypatch.setenv("DB_NAME", "test_db")

    # ✅ Now import the app AFTER env vars are set
    import app.main as app_main

    # ✅ Override engine in the app module
    monkeypatch.setattr(app_main, "engine", engine)

    # ✅ Build TestClient from app_main.app instead of global app
    with TestClient(app_main.app) as c:
        yield c
