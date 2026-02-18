import re
from decimal import Decimal

from models.bank_account import BankAccount
from models.dream import Dream, DreamMilestone
from sqlalchemy import func
from sqlalchemy.orm import Session


def _compute_progress_percent(
    total_amount: Decimal | None,
    target_amount: Decimal | None,
) -> Decimal:
    total = Decimal(total_amount or 0)
    target = Decimal(target_amount or 0)

    if target <= 0:
        return Decimal("0")

    percent = (total / target) * Decimal("100")
    if percent > Decimal("100"):
        return Decimal("100")
    if percent < Decimal("0"):
        return Decimal("0")
    return percent.quantize(Decimal("0.01"))


def _extract_currency_from_title(title: str | None) -> Decimal | None:
    if not title:
        return None

    # Aceita formatos como: R$ 100.000, R$100000, R$ 1.000.000,50
    pattern = r"R\$\s*([\d\.\,]+)"
    match = re.search(pattern, title, flags=re.IGNORECASE)
    if not match:
        return None

    raw_value = match.group(1).strip()
    normalized = raw_value.replace(".", "").replace(",", ".")
    try:
        value = Decimal(normalized)
    except Exception:
        return None
    return value if value > 0 else None


def sync_dream_milestone_financial_progress(
    db: Session,
    user_id: int,
    dream_id: int,
) -> Decimal:
    dream = (
        db.query(Dream)
        .filter(
            Dream.id == dream_id,
            Dream.user_id == user_id,
        )
        .first()
    )
    if not dream:
        return Decimal("0")

    total_amount = (
        db.query(func.coalesce(func.sum(BankAccount.total_value), 0))
        .filter(
            BankAccount.user_id == user_id,
            BankAccount.objective_dream_id == dream_id,
        )
        .scalar()
    )

    progress_percent = _compute_progress_percent(
        total_amount=total_amount,
        target_amount=dream.smart_financial_target_value,
    )

    milestones = (
        db.query(DreamMilestone).filter(DreamMilestone.dream_id == dream_id).all()
    )
    for milestone in milestones:
        extracted_target = _extract_currency_from_title(milestone.title)
        if milestone.financial_target_value is None and extracted_target is not None:
            # Persiste a meta inferida para evitar recalculo recorrente
            # e permitir exibicao no frontend.
            milestone.financial_target_value = extracted_target

        milestone_target = (
            Decimal(milestone.financial_target_value)
            if milestone.financial_target_value is not None
            else extracted_target
        )
        if milestone_target is None:
            milestone_target = (
                Decimal(dream.smart_financial_target_value)
                if dream.smart_financial_target_value is not None
                else None
            )

        milestone.progress_percent = _compute_progress_percent(
            total_amount=total_amount,
            target_amount=milestone_target,
        )

    return progress_percent
