from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Gera payload único para cada teste
def make_user_payload(username_suffix="1"):
    return {
        "username": f"user_{username_suffix}",
        "email": f"user_{username_suffix}@example.com",
        "password_hash": "abc123"
    }


def test_create_user(client):
    payload = make_user_payload("create")
    r = client.post("/users/", json=payload)

    assert r.status_code == 201
    data = r.json()

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "created_at" in data


def test_list_users(client):
    r = client.get("/users/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_user_by_id(client):
    payload = make_user_payload("getid")

    r = client.post("/users/", json=payload)
    assert r.status_code == 201
    new_user = r.json()

    r2 = client.get(f"/users/{new_user['id']}")
    assert r2.status_code == 200
    assert r2.json()["email"] == payload["email"]


def test_duplicate_email_not_allowed(client):
    payload = make_user_payload("dup")

    r1 = client.post("/users/", json=payload)
    assert r1.status_code == 201

    # tenta criar outro com mesmo email
    payload2 = make_user_payload("dup")
    r2 = client.post("/users/", json=payload2)

    assert r2.status_code == 400
    assert r2.json()["detail"] == "Email already registered"


def test_delete_user(client):
    payload = make_user_payload("delete")
    r = client.post("/users/", json=payload)
    assert r.status_code == 201
    new_user = r.json()

    r = client.delete(f"/users/{new_user['id']}")
    assert r.status_code == 204

    r2 = client.get(f"/users/{new_user['id']}")
    assert r2.status_code == 404


def test_validation_invalid_email(client):
    bad_payload = {
        "username": "abc",
        "email": "email-invalido",
        "password_hash": "123"
    }

    r = client.post("/users/", json=bad_payload)
    assert r.status_code == 422
