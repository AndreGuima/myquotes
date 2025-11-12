import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# ✅ Adiciona o caminho do backend no sys.path
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

# ✅ Importa os módulos principais
from app.main import app
import app.database as app_db
from app.models.user import User
from app.models.quote import Quote
from app.database import Base, get_db


@pytest.fixture(scope="session")
def engine():
    """
    Cria um engine SQLite em memória compartilhada,
    garantindo que o FastAPI e os testes usem o mesmo banco.
    """
    SQLALCHEMY_DATABASE_URL = "sqlite:///file::memory:?cache=shared"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False, "uri": True},
    )

    # 🔹 Força o registro das models antes de criar as tabelas
    _ = (User, Quote)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_sessionmaker(engine):
    """Cria o SessionLocal conectado ao engine de teste."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="function")
def client(engine, db_sessionmaker, monkeypatch):
    """
    Cria um TestClient FastAPI com banco SQLite compartilhado em memória.
    """
    # ⚙️ Substitui engine e SessionLocal dentro do app
    monkeypatch.setattr(app_db, "engine", engine)
    monkeypatch.setattr(app_db, "SessionLocal", db_sessionmaker)

    # 🔁 Sobrescreve dependência get_db
    def override_get_db():
        db = db_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c
