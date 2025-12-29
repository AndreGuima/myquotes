def test_get_quotes_returns_list(client):
    r = client.get("/quotes")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_post_quote_and_get(client):
    payload = {"author": "Unit Tester", "text": "This is a test quote."}
    r = client.post("/quotes", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["author"] == payload["author"]
    assert data["text"] == payload["text"]
    new_id = data["id"]

    r2 = client.get(f"/quotes/{new_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == new_id


def test_update_quote(client):
    # create first
    payload = {"author": "Old Name", "text": "Old text"}
    r = client.post("/quotes", json=payload)
    quote_id = r.json()["id"]

    update_payload = {"author": "New Name"}
    r2 = client.put(f"/quotes/{quote_id}", json=update_payload)
    assert r2.status_code == 200
    assert r2.json()["author"] == "New Name"
    assert r2.json()["text"] == "Old text"  # unchanged field


def test_delete_quote(client):
    payload = {"author": "To Delete", "text": "Bye!"}
    r = client.post("/quotes", json=payload)
    quote_id = r.json()["id"]

    r2 = client.delete(f"/quotes/{quote_id}")
    assert r2.status_code == 204

    r3 = client.get(f"/quotes/{quote_id}")
    assert r3.status_code == 404


def test_validation(client):
    # text vazio ainda deve falhar
    r = client.post("/quotes", json={"author": "", "text": ""})
    assert r.status_code == 422

    # ausência total ainda deve falhar (text obrigatório)
    r = client.post("/quotes", json={})
    assert r.status_code == 422


def test_create_quote_without_author(client):
    payload = {"text": "Quote sem autor"}
    r = client.post("/quotes", json=payload)

    assert r.status_code == 201
    data = r.json()
    assert data["author"] == "Desconhecido"
    assert data["text"] == payload["text"]


def test_create_quote_with_empty_author(client):
    payload = {"author": "", "text": "Autor vazio"}
    r = client.post("/quotes", json=payload)

    assert r.status_code == 201
    assert r.json()["author"] == "Desconhecido"


def test_update_quote_clear_author_sets_default(client):
    # cria
    payload = {"author": "Alguém", "text": "Texto"}
    r = client.post("/quotes", json=payload)
    quote_id = r.json()["id"]

    # limpa autor
    update_payload = {"author": ""}
    r2 = client.put(f"/quotes/{quote_id}", json=update_payload)

    assert r2.status_code == 200
    assert r2.json()["author"] == "Desconhecido"


def test_update_quote_without_author_keeps_existing(client):
    payload = {"author": "Autor Original", "text": "Texto original"}
    r = client.post("/quotes", json=payload)
    quote_id = r.json()["id"]

    update_payload = {"text": "Texto alterado"}
    r2 = client.put(f"/quotes/{quote_id}", json=update_payload)

    assert r2.status_code == 200
    assert r2.json()["author"] == "Autor Original"
    assert r2.json()["text"] == "Texto alterado"
