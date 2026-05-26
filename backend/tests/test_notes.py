def test_notes_crud(client):
    create_response = client.post(
        "/notes",
        json={"title": "Ideias", "content": "Comprar Tesouro Selic"},
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Ideias"
    assert created["content"] == "Comprar Tesouro Selic"

    list_response = client.get("/notes")
    assert list_response.status_code == 200
    assert [note["id"] for note in list_response.json()] == [created["id"]]

    update_response = client.patch(
        f"/notes/{created['id']}",
        json={"title": "Planejamento", "content": "Revisar aportes mensais"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Planejamento"
    assert updated["content"] == "Revisar aportes mensais"

    delete_response = client.delete(f"/notes/{created['id']}")
    assert delete_response.status_code == 204

    assert client.get("/notes").json() == []


def test_notes_validate_empty_content(client):
    response = client.post("/notes", json={"title": " ", "content": " "})

    assert response.status_code in (400, 422)
