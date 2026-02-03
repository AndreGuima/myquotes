from datetime import date

from fastapi.testclient import TestClient


def test_create_and_list_reading_list(client: TestClient):
    payload = {
        "title": "O Guia do Mochileiro das Galáxias",
        "author": "Douglas Adams",
        "status": "to_read",
    }
    r = client.post("/reading-list", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "to_read"

    r2 = client.get("/reading-list")
    assert r2.status_code == 200
    assert any(b["title"] == payload["title"] for b in r2.json())


def test_rating_requires_read_status(client: TestClient):
    payload = {
        "title": "Clean Architecture",
        "status": "reading",
        "rating": 5,
    }
    r = client.post("/reading-list", json=payload)
    assert r.status_code == 201

    r2 = client.post(
        "/reading-list",
        json={"title": "Clean Code", "status": "to_read"},
    )
    assert r2.status_code == 201
    book_id = r2.json()["id"]

    r3 = client.patch(f"/reading-list/{book_id}", json={"rating": 4})
    assert r3.status_code == 400


def test_upsert_daily_log(client: TestClient):
    r = client.post(
        "/reading-list",
        json={"title": "Deep Work", "status": "reading"},
    )
    assert r.status_code == 201
    book_id = r.json()["id"]

    payload = {"comment": "Li 10 páginas hoje", "log_date": date.today().isoformat()}
    r2 = client.post(f"/reading-list/{book_id}/logs", json=payload)
    assert r2.status_code == 200
    assert r2.json()["comment"] == payload["comment"]

    r3 = client.post(
        f"/reading-list/{book_id}/logs",
        json={"comment": "Li mais 5 páginas", "log_date": payload["log_date"]},
    )
    assert r3.status_code == 200
    assert r3.json()["comment"] == "Li mais 5 páginas"
