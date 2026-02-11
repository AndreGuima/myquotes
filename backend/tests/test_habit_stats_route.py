from datetime import date

from services.habit_log_service import HabitLogService


def test_get_habit_stats_route(client, db_sessionmaker):
    # cria hábito via API
    r = client.post(
        "/habits/",
        json={"title": "Hábito Teste", "start_time": "00:00"},
    )
    habit_id = r.json()["id"]

    # cria log usando a MESMA infra da aplicação
    db = db_sessionmaker()
    HabitLogService.toggle_today(
        db,
        user_id=1,
        habit_id=habit_id,
    )
    db.close()

    response = client.get(f"/habits/{habit_id}/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["today_completed"] is True
    assert data["current_streak"] == 1
