import pytest


def test_create_habit(client):
    response = client.post(
        "/habits/",
        json={"title": "Praticar inglês", "start_time": "07:00"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Praticar inglês"
    assert data["is_active"] is True


def test_list_only_active_habits(client):
    client.post("/habits/", json={"title": "Beber água", "start_time": "07:00"})

    response = client.post(
        "/habits/",
        json={"title": "Alongar", "start_time": "08:00"},
    )
    habit_id = response.json()["id"]

    delete_response = client.delete(f"/habits/{habit_id}/")
    assert delete_response.status_code == 204

    response = client.get("/habits/")
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Beber água"


def test_list_habits_with_stats(client):
    r = client.post("/habits/", json={"title": "Beber água"})
    habit_id = r.json()["id"]

    client.post(f"/habits/{habit_id}/toggle")

    response = client.get("/habits/?include_stats=true")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == habit_id
    assert data[0]["stats"]["today_completed"] is True


def test_disable_habit(client):
    response = client.post(
        "/habits/",
        json={"title": "Dormir cedo", "start_time": "22:00"},
    )
    habit_id = response.json()["id"]

    delete_response = client.delete(f"/habits/{habit_id}/")
    assert delete_response.status_code == 204

    list_response = client.get("/habits/")
    assert list_response.json() == []


def test_update_habit_title(client):
    response = client.post(
        "/habits/",
        json={"title": "Estudar", "start_time": "19:00"},
    )
    habit_id = response.json()["id"]

    update_response = client.put(
        f"/habits/{habit_id}/",
        json={"title": "Estudar Python"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Estudar Python"


def test_weekly_habit_requires_weekdays(client):
    response = client.post(
        "/habits/",
        json={
            "title": "Academia",
            "frequency_type": "weekly",
        },
    )

    assert response.status_code == 422


def test_create_habit_allows_overnight_time_range(client):
    response = client.post(
        "/habits/",
        json={
            "title": "Dormir 8h",
            "start_time": "22:30",
            "end_time": "06:30",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["start_time"].startswith("22:30")
    assert data["end_time"].startswith("06:30")


def test_create_weekly_habit_with_weekdays(client):
    response = client.post(
        "/habits/",
        json={
            "title": "Academia",
            "frequency_type": "weekly",
            "weekdays": [1, 3, 5],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["frequency_type"] == "weekly"
    assert data["weekdays"] == [1, 3, 5]
    assert data["target_per_week"] == 3
