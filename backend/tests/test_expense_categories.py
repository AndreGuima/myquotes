from fastapi.testclient import TestClient
from models.user import User


def test_expense_categories_crud(client: TestClient):
    create_res = client.post(
        "/expense-categories",
        json={"name": "Alimentacao"},
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["name"] == "Alimentacao"

    list_res = client.get("/expense-categories")
    assert list_res.status_code == 200
    listed = list_res.json()
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]

    duplicate_res = client.post(
        "/expense-categories",
        json={"name": "Alimentacao"},
    )
    assert duplicate_res.status_code == 400
    assert duplicate_res.json()["detail"] == "Categoria já existe"

    update_res = client.patch(
        f"/expense-categories/{created['id']}",
        json={"name": "Mercado"},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Mercado"

    delete_res = client.delete(f"/expense-categories/{created['id']}")
    assert delete_res.status_code == 204

    list_after_delete_res = client.get("/expense-categories")
    assert list_after_delete_res.status_code == 200
    assert list_after_delete_res.json() == []


def test_cannot_access_expense_category_from_other_user(client: TestClient, db_session):
    other_user = User(
        id=2,
        username="other",
        email="other-category@example.com",
        password_hash="hash",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(other_user)
    db_session.flush()

    from models.expense_category import ExpenseCategory

    foreign_category = ExpenseCategory(user_id=other_user.id, name="Categoria de outro")
    db_session.add(foreign_category)
    db_session.commit()

    list_res = client.get("/expense-categories")
    assert list_res.status_code == 200
    assert list_res.json() == []

    update_res = client.patch(
        f"/expense-categories/{foreign_category.id}",
        json={"name": "Novo nome"},
    )
    assert update_res.status_code == 404

    delete_res = client.delete(f"/expense-categories/{foreign_category.id}")
    assert delete_res.status_code == 404


def test_cannot_delete_category_in_use(client: TestClient):
    dream_res = client.post(
        "/dreams",
        json={
            "title": "Reserva",
            "milestones": [],
        },
    )
    assert dream_res.status_code == 201
    dream_id = dream_res.json()["id"]

    account_res = client.post(
        "/bank-accounts",
        json={
            "name": "Conta",
            "objective_dream_id": dream_id,
            "total_value": "1000.00",
        },
    )
    assert account_res.status_code == 201
    account_id = account_res.json()["id"]

    category_res = client.post(
        "/expense-categories",
        json={"name": "Moradia"},
    )
    assert category_res.status_code == 201
    category_id = category_res.json()["id"]

    expense_res = client.post(
        "/expenses",
        json={
            "value": "1200.00",
            "description": "Aluguel",
            "expense_category_id": category_id,
            "payment_method": "debit",
            "bank_account_id": account_id,
            "credit_card_id": None,
            "launch_date": "2026-02-20",
        },
    )
    assert expense_res.status_code == 201

    delete_res = client.delete(f"/expense-categories/{category_id}")
    assert delete_res.status_code == 400
