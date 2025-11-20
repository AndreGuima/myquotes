from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Não existe mais POST /users/, então removemos testes que criavam usuário aqui.


def test_list_users(client):
    r = client.get("/users/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_user_by_id(client):
    """
    Em vez de criar um usuário via POST /users/ (que não existe mais),
    vamos usar o usuário fake criado no conftest.py (id=1)
    """
    r = client.get("/users/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1
    assert r.json()["email"] == "test@example.com"



def test_delete_user(client):
    """
    Antes deletava um criado via POST. Agora deletamos o fake_user (id=1),
    e o GET depois deve retornar 404
    """

    r = client.delete("/users/1")
    assert r.status_code == 204

    # Agora o usuário 1 deve não existir mais
    r2 = client.get("/users/1")
    assert r2.status_code == 404

