from datetime import datetime, timedelta

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.bank_account import BankAccount
from models.dream import Dream
from models.patrimony_snapshot import PatrimonySnapshot
from models.user import User
from schemas.bank_account import (
    BankAccountCreate,
    BankAccountRead,
    BankAccountUpdate,
    PatrimonySnapshotRead,
)
from services.dream_financial_progress import sync_dream_milestone_financial_progress
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/bank-accounts", tags=["Bank Accounts"])


def _to_response(account: BankAccount) -> BankAccountRead:
    return BankAccountRead(
        id=account.id,
        name=account.name,
        objective_dream_id=account.objective_dream_id,
        objective_dream_title=account.objective_dream.title,
        total_value=account.total_value,
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


def _validate_dream_belongs_to_user(db: Session, user_id: int, dream_id: int) -> Dream:
    dream = (
        db.query(Dream)
        .filter(
            Dream.id == dream_id,
            Dream.user_id == user_id,
        )
        .first()
    )
    if not dream:
        raise HTTPException(status_code=400, detail="Objetivo inválido")
    return dream


def _capture_patrimony_snapshot(db: Session, user_id: int) -> None:
    total = (
        db.query(func.coalesce(func.sum(BankAccount.total_value), 0))
        .filter(BankAccount.user_id == user_id)
        .scalar()
    )
    db.add(PatrimonySnapshot(user_id=user_id, total_value=total))


def _get_user_account_or_404(db: Session, user_id: int, account_id: int) -> BankAccount:
    account = (
        db.query(BankAccount)
        .options(joinedload(BankAccount.objective_dream))
        .filter(BankAccount.id == account_id, BankAccount.user_id == user_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
    return account


@router.get("", response_model=list[BankAccountRead])
def list_accounts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    accounts = (
        db.query(BankAccount)
        .options(joinedload(BankAccount.objective_dream))
        .filter(BankAccount.user_id == user.id)
        .order_by(BankAccount.created_at.desc(), BankAccount.id.desc())
        .all()
    )
    return [_to_response(account) for account in accounts]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BankAccountRead)
def create_account(
    payload: BankAccountCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dream = _validate_dream_belongs_to_user(db, user.id, payload.objective_dream_id)

    account = BankAccount(
        user_id=user.id,
        name=payload.name.strip(),
        objective_dream_id=dream.id,
        total_value=payload.total_value,
    )

    if not account.name:
        raise HTTPException(status_code=400, detail="Nome é obrigatório")

    db.add(account)
    db.flush()
    sync_dream_milestone_financial_progress(db, user.id, account.objective_dream_id)
    _capture_patrimony_snapshot(db, user.id)
    db.commit()

    account = _get_user_account_or_404(db, user.id, account.id)
    return _to_response(account)


@router.patch("/{account_id}", response_model=BankAccountRead)
def update_account(
    account_id: int,
    payload: BankAccountUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    account = _get_user_account_or_404(db, user.id, account_id)
    previous_dream_id = account.objective_dream_id

    if payload.name is not None:
        clean_name = payload.name.strip()
        if not clean_name:
            raise HTTPException(status_code=400, detail="Nome é obrigatório")
        account.name = clean_name

    if payload.objective_dream_id is not None:
        dream = _validate_dream_belongs_to_user(db, user.id, payload.objective_dream_id)
        account.objective_dream_id = dream.id

    if payload.total_value is not None:
        account.total_value = payload.total_value

    db.flush()
    sync_dream_milestone_financial_progress(db, user.id, account.objective_dream_id)
    if previous_dream_id != account.objective_dream_id:
        sync_dream_milestone_financial_progress(db, user.id, previous_dream_id)
    _capture_patrimony_snapshot(db, user.id)
    db.commit()

    account = _get_user_account_or_404(db, user.id, account.id)
    return _to_response(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    account = _get_user_account_or_404(db, user.id, account_id)
    dream_id = account.objective_dream_id
    db.delete(account)
    db.flush()
    sync_dream_milestone_financial_progress(db, user.id, dream_id)
    _capture_patrimony_snapshot(db, user.id)
    db.commit()
    return None


@router.get("/patrimony-snapshots", response_model=list[PatrimonySnapshotRead])
def list_patrimony_snapshots(
    days: int = 365,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if days < 7 or days > 3650:
        raise HTTPException(
            status_code=400,
            detail="days must be between 7 and 3650",
        )

    from_dt = datetime.now() - timedelta(days=days - 1)
    snapshots = (
        db.query(PatrimonySnapshot)
        .filter(
            PatrimonySnapshot.user_id == user.id,
            PatrimonySnapshot.snapshot_at >= from_dt,
        )
        .order_by(PatrimonySnapshot.snapshot_at.asc(), PatrimonySnapshot.id.asc())
        .all()
    )
    return snapshots
