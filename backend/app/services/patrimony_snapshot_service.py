from datetime import datetime
from decimal import Decimal

from models.bank_account import BankAccount
from models.patrimony_snapshot import PatrimonySnapshot
from models.patrimony_snapshot_account import PatrimonySnapshotAccount
from sqlalchemy import func
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


def _format_brl(value: Decimal) -> str:
    amount = Decimal(value or ZERO).quantize(Decimal("0.01"))
    formatted = (
        f"{abs(amount):,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace(
            "X",
            ".",
        )
    )
    prefix = "-R$ " if amount < ZERO else "R$ "
    return f"{prefix}{formatted}"


def _previous_month_range(now: datetime) -> tuple[datetime, datetime]:
    current_month_start = datetime(now.year, now.month, 1)
    if now.month == 1:
        previous_month_start = datetime(now.year - 1, 12, 1)
    else:
        previous_month_start = datetime(now.year, now.month - 1, 1)
    return previous_month_start, current_month_start


def get_current_patrimony_total(db: Session, user_id: int) -> Decimal:
    total = (
        db.query(func.coalesce(func.sum(BankAccount.total_value), ZERO))
        .filter(BankAccount.user_id == user_id)
        .scalar()
    )
    return Decimal(total or ZERO)


def get_previous_month_patrimony_total(
    db: Session,
    user_id: int,
    now: datetime | None = None,
) -> Decimal | None:
    previous_month_start, current_month_start = _previous_month_range(
        now or datetime.now(),
    )
    snapshot = (
        db.query(PatrimonySnapshot)
        .filter(
            PatrimonySnapshot.user_id == user_id,
            PatrimonySnapshot.snapshot_at >= previous_month_start,
            PatrimonySnapshot.snapshot_at < current_month_start,
        )
        .order_by(PatrimonySnapshot.snapshot_at.desc(), PatrimonySnapshot.id.desc())
        .first()
    )
    if not snapshot:
        return None
    return Decimal(snapshot.total_value or ZERO)


def build_patrimony_email_context(
    db: Session,
    user_id: int,
    now: datetime | None = None,
) -> dict[str, str]:
    current_total = get_current_patrimony_total(db, user_id)
    previous_total = get_previous_month_patrimony_total(db, user_id, now)

    context = {
        "patrimony_total_label": _format_brl(current_total),
    }

    if previous_total is None:
        context["patrimony_comparison_label"] = (
            "Ainda não há montante do mês passado para comparar."
        )
        return context

    delta = current_total - previous_total
    if delta > ZERO:
        context["patrimony_comparison_label"] = (
            f"Você tem {_format_brl(delta)} a mais que o mês passado."
        )
    elif delta < ZERO:
        context["patrimony_comparison_label"] = (
            f"Você tem {_format_brl(abs(delta))} a menos que o mês passado."
        )
    else:
        context["patrimony_comparison_label"] = (
            "Você está com o mesmo montante do mês passado."
        )

    return context
