from datetime import date


def test_toggle_habit_creates_log(client):
    r = client.post("/habits/", json={"title": "Beber água"})
    habit_id = r.json()["id"]

    response = client.post(f"/habits/{habit_id}/toggle")
    assert response.status_code == 200

    data = response.json()

    assert "log" in data
    assert "stats" in data

    assert data["log"]["habit_id"] == habit_id
    assert data["log"]["date"] == date.today().isoformat()
    assert data["log"]["completed"] is True

    assert data["stats"]["today_completed"] is True
    assert data["stats"]["current_streak"] == 1


def test_toggle_habit_flips_completed(client):
    r = client.post("/habits/", json={"title": "Alongar"})
    habit_id = r.json()["id"]

    r1 = client.post(f"/habits/{habit_id}/toggle")
    assert r1.json()["log"]["completed"] is True
    assert r1.json()["stats"]["current_streak"] == 1

    r2 = client.post(f"/habits/{habit_id}/toggle")
    assert r2.json()["log"]["completed"] is False
    assert r2.json()["stats"]["today_completed"] is False
    assert r2.json()["stats"]["current_streak"] == 0

    r3 = client.post(f"/habits/{habit_id}/toggle")
    assert r3.json()["log"]["completed"] is True
    assert r3.json()["stats"]["current_streak"] == 1


def test_toggle_nonexistent_habit(client):
    response = client.post("/habits/999/toggle")
    assert response.status_code == 400


def test_toggle_returns_log_and_stats(client):
    r = client.post("/habits/", json={"title": "Beber água"})
    habit_id = r.json()["id"]

    response = client.post(f"/habits/{habit_id}/toggle")
    assert response.status_code == 200

    data = response.json()

    assert "log" in data
    assert "stats" in data

    assert data["log"]["completed"] is True
    assert data["log"]["date"] == date.today().isoformat()

    assert data["stats"]["today_completed"] is True
    assert data["stats"]["current_streak"] == 1


def test_toggle_updates_stats(client):
    r = client.post("/habits/", json={"title": "Alongar"})
    habit_id = r.json()["id"]

    r1 = client.post(f"/habits/{habit_id}/toggle")
    assert r1.json()["stats"]["today_completed"] is True

    r2 = client.post(f"/habits/{habit_id}/toggle")
    assert r2.json()["stats"]["today_completed"] is False
    assert r2.json()["stats"]["current_streak"] == 0
