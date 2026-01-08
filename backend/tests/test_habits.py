import pytest


def test_create_habit(client):
    payload = {
        "title": "Praticar inglês",
        "frequency_type": "daily",
    }

    response = client.post("/habits/", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Praticar inglês"
    assert data["frequency_type"] == "daily"
    assert data["is_active"] is True


def test_list_only_active_habits(client):
    # cria hábito ativo
    client.post(
        "/habits/",
        json={"title": "Beber água"},
    )

    # cria outro hábito
    response = client.post(
        "/habits/",
        json={"title": "Alongar"},
    )
    habit_id = response.json()["id"]

    # desativa o segundo
    delete_response = client.delete(f"/habits/{habit_id}")
    assert delete_response.status_code == 204

    # lista hábitos
    response = client.get("/habits/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Beber água"


def test_disable_habit(client):
    response = client.post(
        "/habits/",
        json={"title": "Dormir cedo"},
    )

    habit_id = response.json()["id"]

    delete_response = client.delete(f"/habits/{habit_id}")
    assert delete_response.status_code == 204

    # não deve aparecer mais na listagem
    list_response = client.get("/habits/")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_update_habit_title(client):
    response = client.post(
        "/habits/",
        json={"title": "Estudar"},
    )

    habit_id = response.json()["id"]

    update_response = client.put(
        f"/habits/{habit_id}",
        json={"title": "Estudar Python"},
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Estudar Python"


def test_weekly_habit_requires_target(client):
    payload = {
        "title": "Academia",
        "frequency_type": "weekly",
    }

    response = client.post("/habits/", json=payload)

    assert response.status_code == 422
