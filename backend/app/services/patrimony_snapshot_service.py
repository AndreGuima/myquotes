from decimal import Decimal

from models.bank_account import BankAccount
from models.patrimony_snapshot import PatrimonySnapshot
from models.patrimony_snapshot_account import PatrimonySnapshotAccount
from sqlalchemy.orm import Session, selectinload

ZERO = Decimal("0.00")


def _build_breakdown_signature(accounts):
    return [
        (
            account.id,
            account.total_value or ZERO,
        )
        for account in sorted(accounts, key=lambda acc: acc.id)
    ]


def capture_patrimony_snapshot(db: Session, user_id: int) -> None:
    accounts = (
        db.query(BankAccount)
        .filter(BankAccount.user_id == user_id)
        .order_by(BankAccount.id.asc())
        .all()
    )

    total = sum(
        ((account.total_value or ZERO) for account in accounts),
        start=ZERO,
    )
    current_signature = _build_breakdown_signature(accounts)
    last_snapshot = (
        db.query(PatrimonySnapshot)
        .options(selectinload(PatrimonySnapshot.accounts))
        .filter(PatrimonySnapshot.user_id == user_id)
        .order_by(PatrimonySnapshot.id.desc())
        .first()
    )
    if last_snapshot:
        last_signature = [
            (
                account.bank_account_id,
                account.total_value or ZERO,
            )
            for account in sorted(
                last_snapshot.accounts,
                key=lambda item: item.bank_account_id or 0,
            )
        ]
        if last_snapshot.total_value == total and last_signature == current_signature:
            return

    snapshot = PatrimonySnapshot(
        user_id=user_id,
        total_value=total,
        has_breakdown=True,
    )
    db.add(snapshot)
    db.flush()

    snapshot.accounts.extend(
        [
            PatrimonySnapshotAccount(
                bank_account_id=account.id,
                account_name=account.name,
                total_value=account.total_value or ZERO,
            )
            for account in accounts
        ]
    )
