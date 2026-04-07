import os
import sys
import warnings
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from dotenv import load_dotenv

# ============================================================================
# Caminhos absolutos
# ============================================================================
TESTS_DIR = Path(__file__).resolve().parent  # backend/tests
APP_DIR = TESTS_DIR.parent / "app"  # backend/app
PROJECT_ROOT = TESTS_DIR.parent.parent  # repo root

# ============================================================================
# Ambiente
# ============================================================================
load_dotenv(PROJECT_ROOT / ".env")
os.environ["TESTING"] = "1"

# ============================================================================
# Warnings (dependências externas)
# ============================================================================
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"jose\\.jwt",
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"jose\\.jwt",
    message=".*utcnow.*",
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"jose",
    message=".*utcnow.*",
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*utcnow.*",
)

# ============================================================================
# Projeto FLAT → backend/app é o root do Python
# ============================================================================
sys.path.insert(0, str(APP_DIR))

# ============================================================================
# Imports da aplicação (flat)
# ============================================================================
import database as app_db
import pytest
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from models.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ============================================================================
# 🧪 Banco de dados SQLite em memória
# ============================================================================
@pytest.fixture(scope="session")
def engine():
    db_path = Path("/tmp") / f"myquotes_test_{uuid4().hex}.sqlite3"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(scope="session")
def db_sessionmaker(engine):
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


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
    test_db.close()

    from core.dependencies import get_current_user

    # Evita DetachedInstanceError: retorna um objeto simples em vez de ORM detached
    fake_current_user = SimpleNamespace(
        id=1,
        username="testuser",
        email="test@example.com",
        role="user",
        is_active=True,
        is_verified=True,
    )

    def override_current_user():
        return fake_current_user

    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_client(engine, db_sessionmaker, monkeypatch):
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

    test_db = db_sessionmaker()
    fake_admin = User(
        id=1,
        username="admin",
        email="admin@example.com",
        password_hash="hashed",
        role="admin",
        is_active=True,
        is_verified=True,
    )
    test_db.add(fake_admin)
    test_db.commit()
    test_db.close()

    from core.dependencies import get_current_user

    fake_current_user = SimpleNamespace(
        id=1,
        username="admin",
        email="admin@example.com",
        role="admin",
        is_active=True,
        is_verified=True,
    )

    def override_current_user():
        return fake_current_user

    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db_session(engine, db_sessionmaker):
    """
    Sessão isolada por teste.
    Sempre faz rollback para evitar vazamento de dados.
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = db_sessionmaker(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
