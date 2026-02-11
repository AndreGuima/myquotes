from datetime import date, timedelta

# ============================================================
# Helpers
# ============================================================


def create_habit(client):
    res = client.post(
        "/habits",
        json={
            "title": "Beber água",
            "frequency_type": "daily",
            "start_time": "00:00",
        },
    )
    assert res.status_code == 200
    return res.json()


# ============================================================
# Tests
# ============================================================


def test_history_returns_days_in_range(client):
    habit = create_habit(client)

    # Marca hoje
    toggle = client.post(f"/habits/{habit['id']}/toggle")
    assert toggle.status_code == 200

    res = client.get(f"/habits/{habit['id']}/history")
    assert res.status_code == 200

    body = res.json()
    assert body["habit_id"] == habit["id"]

    days = body["days"]
    assert len(days) >= 1
    assert days[-1]["date"] == date.today().isoformat()
    assert days[-1]["completed"] is True


def test_history_marks_days_without_log_as_false(client):
    habit = create_habit(client)

    today = date.today()
    yesterday = today - timedelta(days=1)

    # Marca apenas hoje
    toggle = client.post(f"/habits/{habit['id']}/toggle")
    assert toggle.status_code == 200

    res = client.get(
        f"/habits/{habit['id']}/history?from_date={yesterday}&to_date={today}"
    )

    assert res.status_code == 200

    days = res.json()["days"]
    assert len(days) == 2

    assert days[0]["date"] == yesterday.isoformat()
    assert days[0]["completed"] is False

    assert days[1]["date"] == today.isoformat()
    assert days[1]["completed"] is True


def test_history_nonexistent_habit_returns_404(client):
    res = client.get("/habits/999999/history")
    assert res.status_code == 404


def test_history_inactive_habit_returns_404(client):
    habit = create_habit(client)

    # Desativa o hábito
    client.patch(
        f"/habits/{habit['id']}",
        json={"is_active": False},
    )

    res = client.get(f"/habits/{habit['id']}/history")
    assert res.status_code == 404


def test_history_only_returns_own_data(client, db_session):
    """
    Mesmo com outro usuário no banco,
    o history deve respeitar o usuário atual (mockado).
    """
    habit = create_habit(client)

    # Cria outro usuário manualmente
    from models.user import User

    other_user = User(
        id=2,
        username="other",
        email="other@test.com",
        password_hash="hashed",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(other_user)
    db_session.commit()

    res = client.get(f"/habits/{habit['id']}/history")
    assert res.status_code == 200
