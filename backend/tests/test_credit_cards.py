from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from models.user import User
from sqlalchemy.exc import IntegrityError


def test_credit_cards_crud(client: TestClient):
    create_res = client.post(
        "/credit-cards",
        json={
            "name": "Nubank Ultravioleta",
        },
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["name"] == "Nubank Ultravioleta"

    list_res = client.get("/credit-cards")
    assert list_res.status_code == 200
    listed = list_res.json()
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]

    update_res = client.patch(
        f"/credit-cards/{created['id']}",
        json={"name": "Nubank Black"},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Nubank Black"

    delete_res = client.delete(f"/credit-cards/{created['id']}")
    assert delete_res.status_code == 204

    list_after_delete_res = client.get("/credit-cards")
    assert list_after_delete_res.status_code == 200
    assert list_after_delete_res.json() == []


def test_credit_cards_cannot_duplicate_name_for_same_user(client: TestClient):
    first = client.post("/credit-cards", json={"name": "Nubank"})
    assert first.status_code == 201

    duplicate = client.post("/credit-cards", json={"name": "Nubank"})
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Cartão já existe"

    other = client.post("/credit-cards", json={"name": "Itau"})
    assert other.status_code == 201

    update_to_duplicate = client.patch(
        f"/credit-cards/{other.json()['id']}",
        json={"name": "Nubank"},
    )
    assert update_to_duplicate.status_code == 400
    assert update_to_duplicate.json()["detail"] == "Cartão já existe"


def test_credit_cards_same_name_allowed_for_different_users(db_session):
    card_name = f"Nubank-{uuid4().hex}"

    own_user = db_session.query(User).filter(User.id == 1).first()
    if own_user is None:
        own_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            role="user",
            is_active=True,
            is_verified=True,
        )
        db_session.add(own_user)
        db_session.flush()

    other_user = User(
        id=2,
        username="other-same-name",
        email="other-same-name@example.com",
        password_hash="hash",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(other_user)
    db_session.commit()

    from models.credit_card import CreditCard

    db_session.add(CreditCard(user_id=other_user.id, name=card_name))
    db_session.commit()

    db_session.add(CreditCard(user_id=1, name=card_name))
    db_session.commit()

    user_1_same_name_count = (
        db_session.query(CreditCard)
        .filter(CreditCard.user_id == 1, CreditCard.name == card_name)
        .count()
    )
    user_2_same_name_count = (
        db_session.query(CreditCard)
        .filter(CreditCard.user_id == other_user.id, CreditCard.name == card_name)
        .count()
    )
    assert user_1_same_name_count == 1
    assert user_2_same_name_count == 1


def test_credit_cards_unique_constraint_enforced_in_database(db_session):
    from models.credit_card import CreditCard

    db_session.add(CreditCard(user_id=1, name="Inter"))
    db_session.commit()

    db_session.add(CreditCard(user_id=1, name="Inter"))
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_cannot_access_credit_card_from_other_user(client: TestClient, db_session):
    other_user = User(
        id=2,
        username="other",
        email="other-card@example.com",
        password_hash="hash",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(other_user)
    db_session.flush()

    from models.credit_card import CreditCard

    foreign_card = CreditCard(user_id=other_user.id, name="Cartao de outro usuario")
    db_session.add(foreign_card)
    db_session.commit()

    list_res = client.get("/credit-cards")
    assert list_res.status_code == 200
    assert list_res.json() == []

    update_res = client.patch(f"/credit-cards/{foreign_card.id}", json={"name": "Novo"})
    assert update_res.status_code == 404

    delete_res = client.delete(f"/credit-cards/{foreign_card.id}")
    assert delete_res.status_code == 404
