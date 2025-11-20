from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def make_register_payload(suffix="1"):
    return {
        "username": f"user_{suffix}",
        "email": f"user_{suffix}@example.com",
        "password": "abc123"
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
    bad = {
        "username": "abc",
        "email": "invalid-email",
        "password": "abc123"
    }
    r = client.post("/auth/register", json=bad)
    assert r.status_code == 422


def test_login_after_register(client):
    payload = make_register_payload("login")

    client.post("/auth/register", json=payload)

    r = client.post("/auth/login", json={
        "username": payload["username"],
        "password": payload["password"]
    })

    assert r.status_code == 200
    assert "access_token" in r.json()
