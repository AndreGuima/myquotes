from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# tests/test_users.py


def test_list_users(client):
    r = client.get("/admin/users/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_user_by_id(client):
    """
    O conftest já cria um usuário fake com id=1
    """
    r = client.get("/admin/users/1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert "username" in data


def test_delete_user(client):
    """
    Agora testamos a deleção lógica do usuário id=1
    """
    r = client.delete("/admin/users/1")
    assert r.status_code == 204

    # Após deleção lógica, o usuário deve aparecer como inativo
    r2 = client.get("/admin/users/1")
    assert r2.status_code == 200
    assert r2.json()["is_active"] is False
