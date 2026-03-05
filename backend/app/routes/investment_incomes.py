from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.bank_account import BankAccount
from models.investment_income import InvestmentIncome
from models.patrimony_snapshot import PatrimonySnapshot
from models.user import User
from schemas.investment_income import (
    InvestmentIncomeCreate,
    InvestmentIncomeRead,
    InvestmentIncomeUpdate,
)
from services.dream_financial_progress import sync_dream_milestone_financial_progress
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/investment-incomes", tags=["Investment Incomes"])


def _to_money_decimal(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_response(item: InvestmentIncome) -> InvestmentIncomeRead:
    return InvestmentIncomeRead(
        id=item.id,
        income_type=item.income_type,
        ticker=item.ticker,
        bank_account_id=item.bank_account_id,
        bank_account_name=item.bank_account.name if item.bank_account else None,
        received_at=item.received_at,
        amount=item.amount,
        notes=item.notes or "",
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _get_user_income_or_404(
    db: Session, user_id: int, income_id: int
) -> InvestmentIncome:
    item = (
        db.query(InvestmentIncome)
        .options(joinedload(InvestmentIncome.bank_account))
        .filter(InvestmentIncome.id == income_id, InvestmentIncome.user_id == user_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Rendimento não encontrado")
    return item


def _get_user_account_or_400(
    db: Session, user_id: int, account_id: int | None, *, for_update: bool = False
) -> BankAccount:
    if account_id is None:
        raise HTTPException(status_code=400, detail="Conta bancária inválida")

    query = db.query(BankAccount).filter(
        BankAccount.id == account_id, BankAccount.user_id == user_id
    )
    if for_update:
        query = query.with_for_update()
    account = query.first()
    if not account:
        raise HTTPException(status_code=400, detail="Conta bancária inválida")
    return account


def _apply_account_delta(account: BankAccount, delta: Decimal) -> None:
    if delta == Decimal("0"):
        return
    current = account.total_value or Decimal("0")
    next_total = _to_money_decimal(current + delta)
    if next_total < Decimal("0"):
        raise HTTPException(status_code=400, detail="Saldo insuficiente na conta")
    account.total_value = next_total


def _capture_patrimony_snapshot(db: Session, user_id: int) -> None:
    total = (
        db.query(func.coalesce(func.sum(BankAccount.total_value), 0))
        .filter(BankAccount.user_id == user_id)
        .scalar()
    )
    db.add(PatrimonySnapshot(user_id=user_id, total_value=total))


@router.get("", response_model=list[InvestmentIncomeRead])
def list_investment_incomes(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=400, detail="'from' must be less than or equal to 'to'"
        )

    query = (
        db.query(InvestmentIncome)
        .options(joinedload(InvestmentIncome.bank_account))
        .filter(InvestmentIncome.user_id == user.id)
    )
    if from_date is not None:
        query = query.filter(InvestmentIncome.received_at >= from_date)
    if to_date is not None:
        query = query.filter(InvestmentIncome.received_at <= to_date)

    items = query.order_by(
        InvestmentIncome.received_at.desc(), InvestmentIncome.id.desc()
    ).all()
    return [_to_response(item) for item in items]


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=InvestmentIncomeRead
)
def create_investment_income(
    payload: InvestmentIncomeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    account = _get_user_account_or_400(
        db, user.id, payload.bank_account_id, for_update=True
    )
    _apply_account_delta(account, _to_money_decimal(payload.amount))

    item = InvestmentIncome(
        user_id=user.id,
        income_type=payload.income_type,
        ticker=payload.ticker.strip().upper(),
        bank_account_id=account.id,
        received_at=payload.received_at,
        amount=_to_money_decimal(payload.amount),
        notes=(payload.notes or "").strip(),
    )

    if not item.ticker:
        raise HTTPException(status_code=400, detail="Ticker é obrigatório")

    db.add(item)
    db.flush()
    _capture_patrimony_snapshot(db, user.id)
    if account.objective_dream_id is not None:
        sync_dream_milestone_financial_progress(db, user.id, account.objective_dream_id)
    db.commit()
    db.expire_all()

    created = _get_user_income_or_404(db, user.id, item.id)
    return _to_response(created)


@router.patch("/{income_id}", response_model=InvestmentIncomeRead)
def update_investment_income(
    income_id: int,
    payload: InvestmentIncomeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = _get_user_income_or_404(db, user.id, income_id)

    next_account_id = (
        payload.bank_account_id
        if payload.bank_account_id is not None
        else item.bank_account_id
    )
    next_amount = (
        _to_money_decimal(payload.amount)
        if payload.amount is not None
        else _to_money_decimal(item.amount)
    )

    if next_account_id is None:
        raise HTTPException(status_code=400, detail="Conta bancária inválida")

    previous_account_id = item.bank_account_id
    previous_amount = _to_money_decimal(item.amount)
    account_deltas: dict[int, Decimal] = {}
    if previous_account_id is not None:
        account_deltas[previous_account_id] = (
            account_deltas.get(previous_account_id, Decimal("0")) - previous_amount
        )
    account_deltas[next_account_id] = (
        account_deltas.get(next_account_id, Decimal("0")) + next_amount
    )

    touched_dream_ids: set[int] = set()
    has_balance_change = False
    for account_id in sorted(account_deltas):
        delta = account_deltas[account_id]
        if delta == Decimal("0"):
            continue
        account = _get_user_account_or_400(db, user.id, account_id, for_update=True)
        _apply_account_delta(account, delta)
        has_balance_change = True
        if account.objective_dream_id is not None:
            touched_dream_ids.add(account.objective_dream_id)

    if payload.income_type is not None:
        item.income_type = payload.income_type
    if payload.ticker is not None:
        clean_ticker = payload.ticker.strip().upper()
        if not clean_ticker:
            raise HTTPException(status_code=400, detail="Ticker é obrigatório")
        item.ticker = clean_ticker
    if payload.received_at is not None:
        item.received_at = payload.received_at
    if payload.amount is not None:
        item.amount = _to_money_decimal(payload.amount)
    if payload.notes is not None:
        item.notes = payload.notes.strip()
    item.bank_account_id = next_account_id

    db.flush()
    if has_balance_change:
        _capture_patrimony_snapshot(db, user.id)
    for dream_id in touched_dream_ids:
        sync_dream_milestone_financial_progress(db, user.id, dream_id)
    db.commit()
    db.expire_all()

    updated = _get_user_income_or_404(db, user.id, income_id)
    return _to_response(updated)


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment_income(
    income_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = _get_user_income_or_404(db, user.id, income_id)

    touched_dream_ids: set[int] = set()
    if item.bank_account_id is not None:
        account = _get_user_account_or_400(
            db, user.id, item.bank_account_id, for_update=True
        )
        _apply_account_delta(account, -_to_money_decimal(item.amount))
        if account.objective_dream_id is not None:
            touched_dream_ids.add(account.objective_dream_id)

    db.delete(item)
    db.flush()
    _capture_patrimony_snapshot(db, user.id)
    for dream_id in touched_dream_ids:
        sync_dream_milestone_financial_progress(db, user.id, dream_id)
    db.commit()
    db.expire_all()
    return None
