import os
import sys
from pathlib import Path

# Ativa modo de teste
os.environ["TESTING"] = "1"

# 👇 backend/app vira o ROOT do Python
APP_PATH = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_PATH))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database as app_db
from database import Base, get_db
from main import app
from models.user import User
from models.quote import Quote


# ============================================================================
# 🧪 Banco de dados SQLite em memória
# ============================================================================
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///file::memory:?cache=shared",
        connect_args={"check_same_thread": False, "uri": True},
    )

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_sessionmaker(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ============================================================================
# 🧪 TestClient
# ============================================================================
@pytest.fixture(scope="function")
def client(engine, db_sessionmaker, monkeypatch):
    # Override engine e SessionLocal
    monkeypatch.setattr(app_db, "engine", engine)
    monkeypatch.setattr(app_db, "SessionLocal", db_sessionmaker)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = db_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Usuário fake
    test_db = db_sessionmaker()
    fake_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed",
        role="user",
        is_active=True,
        is_verified=True,
    )
    test_db.add(fake_user)
    test_db.commit()

    from core.dependencies import get_current_user

    def override_current_user():
        return fake_user

    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session(db_sessionmaker):
    """Sessão de banco usada diretamente pelos testes."""
    session = db_sessionmaker()
    try:
        yield session
    finally:
        session.close()
