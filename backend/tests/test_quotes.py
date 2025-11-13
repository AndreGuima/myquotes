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
    r = client.post("/quotes", json={"author": "", "text": ""})
    assert r.status_code == 422

    r = client.post("/quotes", json={})
    assert r.status_code == 422
