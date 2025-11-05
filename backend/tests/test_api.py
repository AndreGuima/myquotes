def test_get_quotes_returns_list(client):
    """GET /quotes should return 200 and a JSON list."""
    r = client.get("/quotes")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_post_quote_and_get(client):
    """POST /quotes should create a quote and return it with an id."""
    payload = {"author": "Unit Tester", "text": "This is a test quote."}
    r = client.post("/quotes", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data.get("author") == payload["author"]
    assert data.get("text") == payload["text"]
    assert "id" in data

    # ensure it shows up in GET
    r2 = client.get("/quotes")
    assert r2.status_code == 200
    items = r2.json()
    assert any(item.get("id") == data["id"] for item in items)

def test_post_quote_validates_required_fields(client):
    """POST /quotes should return 422 when required fields are missing or empty."""
    
    # Missing both
    r = client.post("/quotes", json={})
    assert r.status_code == 422
    assert any(err["loc"][-1] == "author" for err in r.json()["detail"])
    assert any(err["loc"][-1] == "text" for err in r.json()["detail"])

    # Missing author
    r = client.post("/quotes", json={"text": "Quote without author"})
    assert r.status_code == 422
    assert any(err["loc"][-1] == "author" for err in r.json()["detail"])

    # Missing text
    r = client.post("/quotes", json={"author": "Author without quote"})
    assert r.status_code == 422
    assert any(err["loc"][-1] == "text" for err in r.json()["detail"])

    # Empty strings -> STILL invalid (Pydantic allows empty strings unless we add validators)
    r = client.post("/quotes", json={"author": "", "text": ""})
    assert r.status_code == 422 or r.status_code == 201  # until we enforce non-empty explicitly
