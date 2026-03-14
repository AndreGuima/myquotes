from fastapi.testclient import TestClient
from models.dream import Dream
from models.user import User


def test_bank_accounts_crud(client: TestClient):
    dream_res = client.post(
        "/dreams",
        json={
            "title": "Comprar casa",
            "milestones": [],
        },
    )
    assert dream_res.status_code == 201
    dream_id = dream_res.json()["id"]

    create_res = client.post(
        "/bank-accounts",
        json={
            "name": "Conta Principal",
            "objective_dream_id": dream_id,
            "total_value": "2500.50",
        },
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["name"] == "Conta Principal"
    assert created["objective_dream_id"] == dream_id
    assert created["objective_dream_title"] == "Comprar casa"
    assert created["total_value"] == "2500.50"

    list_res = client.get("/bank-accounts")
    assert list_res.status_code == 200
    listed = list_res.json()
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]

    update_res = client.patch(
        f"/bank-accounts/{created['id']}",
        json={"name": "Conta Corrente", "total_value": "3000.00"},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Conta Corrente"
    assert updated["total_value"] == "3000.00"

    delete_res = client.delete(f"/bank-accounts/{created['id']}")
    assert delete_res.status_code == 204

    list_after_delete_res = client.get("/bank-accounts")
    assert list_after_delete_res.status_code == 200
    assert list_after_delete_res.json() == []


def test_cannot_link_bank_account_to_other_user_dream(client: TestClient, db_session):
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

    foreign_dream = Dream(user_id=other_user.id, title="Sonho de outro usuário")
    db_session.add(foreign_dream)
    db_session.commit()

    res = client.post(
        "/bank-accounts",
        json={
            "name": "Conta indevida",
            "objective_dream_id": foreign_dream.id,
            "total_value": "100.00",
        },
    )
    assert res.status_code == 400


def test_patrimony_snapshots_are_created_and_listed(client: TestClient):
    dream_res = client.post(
        "/dreams",
        json={
            "title": "Reserva",
            "milestones": [],
        },
    )
    assert dream_res.status_code == 201
    dream_id = dream_res.json()["id"]

    create_res = client.post(
        "/bank-accounts",
        json={
            "name": "Conta Snapshot",
            "objective_dream_id": dream_id,
            "total_value": "100.00",
        },
    )
    assert create_res.status_code == 201
    account_id = create_res.json()["id"]

    update_res = client.patch(
        f"/bank-accounts/{account_id}",
        json={"total_value": "250.00"},
    )
    assert update_res.status_code == 200

    list_res = client.get("/bank-accounts/patrimony-snapshots")
    assert list_res.status_code == 200
    snapshots = list_res.json()
    assert len(snapshots) >= 2
    assert all("snapshot_at" in snapshot for snapshot in snapshots)
    assert snapshots[-1]["total_value"] == "250.00"
    assert snapshots[-1]["has_breakdown"] is True
    assert snapshots[-1]["accounts"] == [
        {
            "bank_account_id": account_id,
            "account_name": "Conta Snapshot",
            "total_value": "250.00",
        }
    ]


def test_patrimony_snapshots_include_multiple_accounts_breakdown(client: TestClient):
    dream_res = client.post(
        "/dreams",
        json={
            "title": "Reserva",
            "milestones": [],
        },
    )
    assert dream_res.status_code == 201
    dream_id = dream_res.json()["id"]

    first_res = client.post(
        "/bank-accounts",
        json={
            "name": "Conta Corrente",
            "objective_dream_id": dream_id,
            "total_value": "100.00",
        },
    )
    assert first_res.status_code == 201

    second_res = client.post(
        "/bank-accounts",
        json={
            "name": "Reserva",
            "objective_dream_id": dream_id,
            "total_value": "50.00",
        },
    )
    assert second_res.status_code == 201

    snapshots_res = client.get("/bank-accounts/patrimony-snapshots")
    assert snapshots_res.status_code == 200
    latest = snapshots_res.json()[-1]

    assert latest["total_value"] == "150.00"
    assert latest["has_breakdown"] is True
    assert latest["accounts"] == [
        {
            "bank_account_id": first_res.json()["id"],
            "account_name": "Conta Corrente",
            "total_value": "100.00",
        },
        {
            "bank_account_id": second_res.json()["id"],
            "account_name": "Reserva",
            "total_value": "50.00",
        },
    ]


def test_patrimony_snapshot_after_delete_has_zero_total(client: TestClient):
    dream_res = client.post(
        "/dreams",
        json={
            "title": "Objetivo para zerar",
            "milestones": [],
        },
    )
    assert dream_res.status_code == 201
    dream_id = dream_res.json()["id"]

    create_res = client.post(
        "/bank-accounts",
        json={
            "name": "Conta a remover",
            "objective_dream_id": dream_id,
            "total_value": "500.00",
        },
    )
    assert create_res.status_code == 201
    account_id = create_res.json()["id"]

    delete_res = client.delete(f"/bank-accounts/{account_id}")
    assert delete_res.status_code == 204

    snapshots_res = client.get("/bank-accounts/patrimony-snapshots")
    assert snapshots_res.status_code == 200
    snapshots = snapshots_res.json()
    assert len(snapshots) >= 2
    assert snapshots[-1]["total_value"] == "0.00"


def test_patrimony_snapshots_days_validation(client: TestClient):
    low_days_res = client.get("/bank-accounts/patrimony-snapshots?days=6")
    assert low_days_res.status_code == 400
    assert low_days_res.json()["detail"] == "days must be between 7 and 3650"

    high_days_res = client.get("/bank-accounts/patrimony-snapshots?days=3651")
    assert high_days_res.status_code == 400
    assert high_days_res.json()["detail"] == "days must be between 7 and 3650"
