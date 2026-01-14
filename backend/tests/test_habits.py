import pytest


def test_create_habit(client):
    response = client.post("/habits/", json={"title": "Praticar inglês"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Praticar inglês"
    assert data["is_active"] is True


def test_list_only_active_habits(client):
    client.post("/habits/", json={"title": "Beber água"})

    response = client.post("/habits/", json={"title": "Alongar"})
    habit_id = response.json()["id"]

    delete_response = client.delete(f"/habits/{habit_id}/")
    assert delete_response.status_code == 204

    response = client.get("/habits/")
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Beber água"


def test_disable_habit(client):
    response = client.post("/habits/", json={"title": "Dormir cedo"})
    habit_id = response.json()["id"]

    delete_response = client.delete(f"/habits/{habit_id}/")
    assert delete_response.status_code == 204

    list_response = client.get("/habits/")
    assert list_response.json() == []


def test_update_habit_title(client):
    response = client.post("/habits/", json={"title": "Estudar"})
    habit_id = response.json()["id"]

    update_response = client.put(
        f"/habits/{habit_id}/",
        json={"title": "Estudar Python"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Estudar Python"


def test_weekly_habit_requires_target(client):
    response = client.post(
        "/habits/",
        json={"title": "Academia", "frequency_type": "weekly"},
    )

    assert response.status_code == 422
