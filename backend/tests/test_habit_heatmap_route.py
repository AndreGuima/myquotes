def test_heatmap_route_ok(client):
    r = client.post("/habits", json={"title": "Heatmap Habit"})
    habit_id = r.json()["id"]

    r = client.get(f"/habits/{habit_id}/heatmap?days=14")
    assert r.status_code == 200

    body = r.json()
    assert body["habit_id"] == habit_id
    assert len(body["days"]) == 14
    assert "count" in body["days"][0]


def test_heatmap_days_validation(client):
    r = client.get("/habits/1/heatmap?days=3")
    assert r.status_code == 400
    assert "days must be between" in r.json()["detail"]


def test_heatmap_nonexistent_habit(client):
    r = client.get("/habits/99999/heatmap")
    assert r.status_code == 404
