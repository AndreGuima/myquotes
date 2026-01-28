from core.security import create_email_verification_token
from fastapi.testclient import TestClient
from main import app
from models.user import User

client = TestClient(app)


def make_register_payload(prefix):
    return {
        "username": f"user_{prefix}",
        "email": f"user_{prefix}@example.com",
        "password": "Abcdef12!",  # ✅ senha válida
        "confirm_password": "Abcdef12!",
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

    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201

    # 🔑 gera token de verificação
    user = db_session.query(User).filter_by(email=payload["email"]).first()
    token = create_email_verification_token(user.id)

    # ✅ verifica email VIA API (mesma infra do login)
    r = client.get(f"/auth/verify-email?token={token}")
    assert r.status_code == 200

    # 🔓 agora o login deve funcionar
    r = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )

    assert r.status_code == 200
    assert "access_token" in r.json()
