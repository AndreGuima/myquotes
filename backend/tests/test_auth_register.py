from app.core.security import create_email_verification_token
from app.main import app
from app.models.user import User
from fastapi.testclient import TestClient

client = TestClient(app)


def make_register_payload(prefix):
    return {
        "username": f"user_{prefix}",
        "email": f"user_{prefix}@example.com",
        "password": "12345678",
        "confirm_password": "12345678",
    }


def test_register_ok(client):
    payload = make_register_payload("ok")
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["user"]["email"] == payload["email"]


def test_register_duplicate_email(client):
    payload = make_register_payload("dup")

    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 400


def test_register_invalid_email(client):
    bad = {"username": "abc", "email": "invalid-email", "password": "abc123"}
    r = client.post("/auth/register", json=bad)
    assert r.status_code == 422


def test_login_after_register(client):
    payload = make_register_payload("login")

    client.post("/auth/register", json=payload)

    r = client.post(
        "/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )

    assert r.status_code == 403  # agora é o comportamento esperado


def test_login_blocked_until_verified(client):
    payload = make_register_payload("block")

    client.post("/auth/register", json=payload)

    r = client.post(
        "/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )

    assert r.status_code == 403
    assert "verificar seu email" in r.json()["detail"]


def test_login_after_email_verified(client, db_session):
    payload = make_register_payload("verify")

    client.post("/auth/register", json=payload)

    # marca como verificado
    user = db_session.query(User).filter_by(email=payload["email"]).first()
    user.is_verified = True
    db_session.commit()

    r = client.post(
        "/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )

    assert r.status_code == 200
    assert "access_token" in r.json()
