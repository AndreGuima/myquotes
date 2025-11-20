import os
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add backend path so imports work
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from app.main import app
import app.database as app_db
from app.database import Base, get_db
from app.models.user import User
from app.models.quote import Quote




# ============================================================================
# 🧪 Banco de dados SQLite em memória (compartilhado)
# ============================================================================
@pytest.fixture(scope="session")
def engine():
    SQLALCHEMY_DATABASE_URL = "sqlite:///file::memory:?cache=shared"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False, "uri": True},
    )

    # Garantir que models estão registradas
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_sessionmaker(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ============================================================================
# 🧪 TestClient com overrides (DB + Auth)
# ============================================================================
@pytest.fixture(scope="function")
def client(engine, db_sessionmaker, monkeypatch):
    # Override engine e SessionLocal dentro do app
    monkeypatch.setattr(app_db, "engine", engine)
    monkeypatch.setattr(app_db, "SessionLocal", db_sessionmaker)

    # =========================================
    # 👉 Reset REAL do banco antes de cada teste
    # =========================================
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # override get_db
    def override_get_db():
        db = db_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # =========================================
    # 👉 Criar usuário fake para autenticação
    # =========================================
    test_db = db_sessionmaker()
    fake_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed",
        role="user"
    )
    test_db.add(fake_user)
    test_db.commit()

    # =========================================
    # 👉 Override get_current_user
    # =========================================
    from app.core.dependencies import get_current_user

    def override_current_user():
        return fake_user

    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as c:
        yield c

