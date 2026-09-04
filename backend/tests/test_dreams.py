from fastapi.testclient import TestClient
from models.habit import Habit
from models.user import User


def test_create_list_and_toggle_milestone(client: TestClient):
    habit_res = client.post("/habits", json={"title": "Treinar corrida"})
    assert habit_res.status_code == 200
    habit_id = habit_res.json()["id"]

    payload = {
        "title": "Correr meia maratona",
        "description": "Meta esportiva de 2026",
        "smart": {
            "targetDate": "2026-12-01",
        },
        "linkedHabitIds": [habit_id],
        "milestones": [
            {"title": "Fechar 10km", "targetDate": "2026-05-01"},
            {"title": "Fechar 15km", "targetDate": "2026-08-01"},
        ],
    }
    create_res = client.post("/dreams", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["title"] == payload["title"]
    assert created["linkedHabitIds"] == [habit_id]
    assert len(created["milestones"]) == 2

    list_res = client.get("/dreams")
    assert list_res.status_code == 200
    dreams = list_res.json()
    assert len(dreams) == 1

    dream_id = created["id"]
    milestone_id = created["milestones"][0]["id"]
    toggle_res = client.post(f"/dreams/{dream_id}/milestones/{milestone_id}/toggle")
    assert toggle_res.status_code == 200
    assert toggle_res.json()["completedAt"] is not None

    update_res = client.patch(
        f"/dreams/{dream_id}",
        json={
            "title": "Correr meia maratona sub 2h",
            "description": "Meta atualizada",
            "smart": {
                "targetDate": "2026-11-10",
            },
            "linkedHabitIds": [habit_id],
            "milestones": [
                {
                    "title": "Longao de 18km",
                    "targetDate": "2026-09-01",
                    "completedAt": toggle_res.json()["completedAt"],
                }
            ],
        },
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["title"] == "Correr meia maratona sub 2h"
    assert len(updated["milestones"]) == 1
    assert updated["milestones"][0]["completedAt"] is not None


def test_cannot_link_other_user_habit(client: TestClient, db_session):
    other_user = User(
        id=2,
        username="other",
        email="other@example.com",
        password_hash="hash",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(other_user)
    db_session.flush()

    foreign_habit = Habit(user_id=other_user.id, title="Hábito de outro usuário")
    db_session.add(foreign_habit)
    db_session.commit()

    res = client.post(
        "/dreams",
        json={
            "title": "Sonho inválido",
            "linkedHabitIds": [foreign_habit.id],
            "milestones": [],
        },
    )
    assert res.status_code == 400


def test_dream_details_returns_financial_remaining_value(client: TestClient):
    create_res = client.post(
        "/dreams",
        json={
            "title": "Reserva de emergencia",
            "smart": {
                "financialTargetValue": "2000.00",
            },
            "milestones": [
                {
                    "title": "Juntar R$ 2.000",
                    "financialTargetValue": "2000.00",
                }
            ],
        },
    )
    assert create_res.status_code == 201
    dream_id = create_res.json()["id"]

    account_res = client.post(
        "/bank-accounts",
        json={
            "name": "Caixinha da reserva",
            "objective_dream_id": dream_id,
            "total_value": "1500.00",
        },
    )
    assert account_res.status_code == 201

    detail_res = client.get(f"/dreams/{dream_id}")
    assert detail_res.status_code == 200
    smart = detail_res.json()["smart"]
    assert smart["financialTargetValue"] == "2000.00"
    assert smart["financialCurrentValue"] == "1500.00"
    assert smart["financialRemainingValue"] == "500.00"
    assert smart["financialProgressPercent"] == "75.00"


def test_update_milestone_current_value_updates_progress(client: TestClient):
    create_res = client.post(
        "/dreams",
        json={
            "title": "Viagem",
            "milestones": [{"title": "Reserva", "financialTargetValue": "1000.00"}],
        },
    )
    assert create_res.status_code == 201
    created = create_res.json()
    dream_id = created["id"]
    milestone_id = created["milestones"][0]["id"]

    update_res = client.patch(
        f"/dreams/{dream_id}/milestones/{milestone_id}",
        json={"financialCurrentValue": "250.00"},
    )

    assert update_res.status_code == 200
    assert update_res.json()["financialCurrentValue"] == "250.00"
    assert update_res.json()["progressPercent"] == "25.00"

    detail_res = client.get(f"/dreams/{dream_id}")
    assert detail_res.json()["milestones"][0]["financialCurrentValue"] == "250.00"
