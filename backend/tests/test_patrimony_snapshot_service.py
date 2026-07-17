from datetime import datetime
from decimal import Decimal

from models.bank_account import BankAccount
from models.dream import Dream
from models.patrimony_snapshot import PatrimonySnapshot
from models.user import User
from services.patrimony_snapshot_service import build_patrimony_email_context


def _create_user_with_dream(db_session):
    user = User(
        username="andre",
        email="andre@example.com",
        password_hash="hashed",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.flush()

    dream = Dream(user_id=user.id, title="Reserva")
    db_session.add(dream)
    db_session.flush()
    return user, dream


def test_build_patrimony_email_context_more_than_previous_month(db_session):
    user, dream = _create_user_with_dream(db_session)
    db_session.add(
        BankAccount(
            user_id=user.id,
            objective_dream_id=dream.id,
            name="Conta Principal",
            total_value=Decimal("500.00"),
        )
    )
    db_session.add(
        PatrimonySnapshot(
            user_id=user.id,
            total_value=Decimal("450.00"),
            snapshot_at=datetime(2026, 4, 30, 12, 0, 0),
            has_breakdown=True,
        )
    )
    db_session.flush()

    context = build_patrimony_email_context(
        db_session,
        user.id,
        now=datetime(2026, 5, 14, 8, 0, 0),
    )

    assert context["patrimony_total_label"] == "R$ 500,00"
    assert (
        context["patrimony_comparison_label"]
        == "Você tem R$ 50,00 a mais que o mês passado."
    )


def test_build_patrimony_email_context_less_than_previous_month(db_session):
    user, dream = _create_user_with_dream(db_session)
    db_session.add(
        BankAccount(
            user_id=user.id,
            objective_dream_id=dream.id,
            name="Conta Principal",
            total_value=Decimal("400.00"),
        )
    )
    db_session.add(
        PatrimonySnapshot(
            user_id=user.id,
            total_value=Decimal("450.00"),
            snapshot_at=datetime(2026, 4, 30, 12, 0, 0),
            has_breakdown=True,
        )
    )
    db_session.flush()

    context = build_patrimony_email_context(
        db_session,
        user.id,
        now=datetime(2026, 5, 14, 8, 0, 0),
    )

    assert context["patrimony_total_label"] == "R$ 400,00"
    assert (
        context["patrimony_comparison_label"]
        == "Você tem R$ 50,00 a menos que o mês passado."
    )


def test_build_patrimony_email_context_with_all_comparisons(db_session):
    user, dream = _create_user_with_dream(db_session)
    db_session.add(
        BankAccount(
            user_id=user.id,
            objective_dream_id=dream.id,
            name="Conta Principal",
            total_value=Decimal("500.00"),
        )
    )
    db_session.add_all(
        [
            PatrimonySnapshot(
                user_id=user.id,
                total_value=Decimal("350.00"),
                snapshot_at=datetime(2025, 5, 14, 18, 0, 0),
                has_breakdown=True,
            ),
            PatrimonySnapshot(
                user_id=user.id,
                total_value=Decimal("400.00"),
                snapshot_at=datetime(2025, 12, 31, 18, 0, 0),
                has_breakdown=True,
            ),
            PatrimonySnapshot(
                user_id=user.id,
                total_value=Decimal("450.00"),
                snapshot_at=datetime(2026, 4, 30, 18, 0, 0),
                has_breakdown=True,
            ),
        ]
    )
    db_session.flush()

    context = build_patrimony_email_context(
        db_session,
        user.id,
        now=datetime(2026, 5, 14, 8, 0, 0),
    )

    assert (
        context["patrimony_comparison_label"]
        == "Você tem R$ 50,00 a mais que o mês passado."
    )
    assert (
        context["patrimony_semester_comparison_label"]
        == "Você tem R$ 100,00 a mais em relação ao semestre passado."
    )
    assert (
        context["patrimony_year_comparison_label"]
        == "Você tem R$ 150,00 a mais em relação ao mesmo dia do ano passado."
    )


def test_same_day_previous_year_uses_latest_snapshot_available_by_that_day(
    db_session,
):
    user, dream = _create_user_with_dream(db_session)
    db_session.add(
        BankAccount(
            user_id=user.id,
            objective_dream_id=dream.id,
            name="Conta Principal",
            total_value=Decimal("500.00"),
        )
    )
    db_session.add_all(
        [
            PatrimonySnapshot(
                user_id=user.id,
                total_value=Decimal("300.00"),
                snapshot_at=datetime(2025, 5, 10, 18, 0, 0),
                has_breakdown=True,
            ),
            PatrimonySnapshot(
                user_id=user.id,
                total_value=Decimal("350.00"),
                snapshot_at=datetime(2025, 5, 15, 8, 0, 0),
                has_breakdown=True,
            ),
        ]
    )
    db_session.flush()

    context = build_patrimony_email_context(
        db_session,
        user.id,
        now=datetime(2026, 5, 14, 8, 0, 0),
    )

    assert (
        context["patrimony_year_comparison_label"]
        == "Você tem R$ 200,00 a mais em relação ao mesmo dia do ano passado."
    )
