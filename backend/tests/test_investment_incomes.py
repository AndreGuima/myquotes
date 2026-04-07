from fastapi.testclient import TestClient


def _create_dream(client: TestClient) -> int:
    res = client.post(
        "/dreams",
        json={
            "title": "Renda passiva",
            "milestones": [],
        },
    )
    assert res.status_code == 201
    return res.json()["id"]


def _create_account(
    client: TestClient,
    dream_id: int,
    name: str,
    total: str,
    *,
    allow_investment_income: bool = True,
) -> int:
    res = client.post(
        "/bank-accounts",
        json={
            "name": name,
            "objective_dream_id": dream_id,
            "total_value": total,
            "allow_investment_income": allow_investment_income,
        },
    )
    assert res.status_code == 201
    return res.json()["id"]


def _get_account_total(client: TestClient, account_id: int) -> str:
    res = client.get("/bank-accounts")
    assert res.status_code == 200
    account = next(item for item in res.json() if item["id"] == account_id)
    return account["total_value"]


def test_investment_incomes_crud_updates_account_balance(client: TestClient):
    dream_id = _create_dream(client)
    account_a_id = _create_account(client, dream_id, "Conta A", "1000.00")
    account_b_id = _create_account(client, dream_id, "Conta B", "500.00")

    create_res = client.post(
        "/investment-incomes",
        json={
            "income_type": "dividend",
            "ticker": "itsa4",
            "bank_account_id": account_a_id,
            "received_at": "2026-03-01",
            "amount": "100.00",
            "notes": "Março",
        },
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["ticker"] == "ITSA4"
    assert created["bank_account_id"] == account_a_id
    assert created["bank_account_name"] == "Conta A"
    assert _get_account_total(client, account_a_id) == "1100.00"

    update_amount_res = client.patch(
        f"/investment-incomes/{created['id']}",
        json={"amount": "150.00"},
    )
    assert update_amount_res.status_code == 200
    assert update_amount_res.json()["amount"] == "150.00"
    assert _get_account_total(client, account_a_id) == "1150.00"

    move_account_res = client.patch(
        f"/investment-incomes/{created['id']}",
        json={
            "bank_account_id": account_b_id,
            "amount": "50.00",
        },
    )
    assert move_account_res.status_code == 200
    moved = move_account_res.json()
    assert moved["bank_account_id"] == account_b_id
    assert moved["bank_account_name"] == "Conta B"
    assert moved["amount"] == "50.00"
    assert _get_account_total(client, account_a_id) == "1000.00"
    assert _get_account_total(client, account_b_id) == "550.00"

    delete_res = client.delete(f"/investment-incomes/{created['id']}")
    assert delete_res.status_code == 204
    assert _get_account_total(client, account_b_id) == "500.00"


def test_investment_income_requires_valid_account(client: TestClient):
    res = client.post(
        "/investment-incomes",
        json={
            "income_type": "dividend",
            "ticker": "BBAS3",
            "bank_account_id": 9999,
            "received_at": "2026-03-01",
            "amount": "10.00",
            "notes": "",
        },
    )
    assert res.status_code == 400


def test_investment_income_requires_account_enabled_for_provents(client: TestClient):
    dream_id = _create_dream(client)
    account_id = _create_account(
        client,
        dream_id,
        "Conta Não Habilitada",
        "1000.00",
        allow_investment_income=False,
    )

    res = client.post(
        "/investment-incomes",
        json={
            "income_type": "dividend",
            "ticker": "ITSA4",
            "bank_account_id": account_id,
            "received_at": "2026-03-01",
            "amount": "10.00",
            "notes": "",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Conta não habilitada para recebimento de proventos"
