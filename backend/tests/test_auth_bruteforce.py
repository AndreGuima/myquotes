from datetime import datetime, timedelta, timezone

import database as app_db
from core.security import hash_password
from models.auth_login_attempt import AuthLoginAttempt
from models.user import User
from services.auth_bruteforce import register_failed_login
from settings import settings


def test_login_bruteforce_lockout(client, monkeypatch):
    monkeypatch.setattr(settings, "BRUTE_FORCE_MAX_ATTEMPTS", 2)
    monkeypatch.setattr(settings, "BRUTE_FORCE_WINDOW_SECONDS", 60)
    monkeypatch.setattr(settings, "BRUTE_FORCE_LOCKOUT_SECONDS", 300)

    session = app_db.SessionLocal()
    user = User(
        username="bfuser",
        email="bfuser@example.com",
        password_hash=hash_password("Correct1!"),
        role="user",
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    session.commit()
    session.close()

    payload = {"email": "bfuser@example.com", "password": "Wrong1!"}

    r1 = client.post("/auth/login", json=payload)
    assert r1.status_code == 401

    r2 = client.post("/auth/login", json=payload)
    assert r2.status_code == 429


def test_successful_login_clears_attempts(client):
    session = app_db.SessionLocal()
    user = User(
        username="clearuser",
        email="clearuser@example.com",
        password_hash=hash_password("Correct1!"),
        role="user",
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    session.commit()
    session.close()

    wrong_payload = {"email": "clearuser@example.com", "password": "Wrong1!"}
    correct_payload = {"email": "clearuser@example.com", "password": "Correct1!"}

    r1 = client.post("/auth/login", json=wrong_payload)
    assert r1.status_code == 401

    r2 = client.post("/auth/login", json=correct_payload)
    assert r2.status_code == 200

    session = app_db.SessionLocal()
    attempt = (
        session.query(AuthLoginAttempt)
        .filter(AuthLoginAttempt.email == "clearuser@example.com")
        .first()
    )
    assert attempt is not None
    assert attempt.attempts == 0
    assert attempt.last_attempt_at is None
    assert attempt.locked_until is None
    session.close()


def test_window_expiration_resets_attempts(db_session, monkeypatch):
    monkeypatch.setattr(settings, "BRUTE_FORCE_MAX_ATTEMPTS", 5)
    monkeypatch.setattr(settings, "BRUTE_FORCE_WINDOW_SECONDS", 60)
    monkeypatch.setattr(settings, "BRUTE_FORCE_LOCKOUT_SECONDS", 300)

    attempt = AuthLoginAttempt(
        email="window@example.com",
        ip_address="127.0.0.1",
        attempts=3,
        last_attempt_at=datetime.now(timezone.utc) - timedelta(seconds=120),
        locked_until=None,
    )
    db_session.add(attempt)
    db_session.commit()

    register_failed_login(db_session, "window@example.com", "127.0.0.1")

    updated = (
        db_session.query(AuthLoginAttempt)
        .filter(AuthLoginAttempt.email == "window@example.com")
        .first()
    )
    assert updated.attempts == 1
    assert updated.last_attempt_at is not None
    assert updated.locked_until is None
