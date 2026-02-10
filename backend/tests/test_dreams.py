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
            "specific": "Completar prova oficial de 21km",
            "measurable": "21km em ate 2h15",
            "achievable": "Treino progressivo com 4 sessoes semanais",
            "relevant": "Melhorar saude e energia",
            "timeBound": "Concluir ate dezembro",
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
    assert dreams[0]["smart"]["specific"] == payload["smart"]["specific"]

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
                "specific": "Completar 21km em prova oficial",
                "measurable": "Abaixo de 2h",
                "achievable": "Treinos consistentes",
                "relevant": "Saude e disciplina",
                "timeBound": "Ate novembro",
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
