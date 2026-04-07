from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from models.bank_account import BankAccount
from models.bank_account_transaction import BankAccountTransaction, TransactionType
from sqlalchemy.orm import Session


def to_money_decimal(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def apply_account_delta(
    db: Session,
    *,
    user_id: int,
    account: BankAccount,
    delta: Decimal,
    transaction_type: TransactionType,
    description: str | None = None,
    transfer_id: int | None = None,
) -> bool:
    normalized_delta = to_money_decimal(delta)
    if normalized_delta == Decimal("0.00"):
        return False

    next_total = to_money_decimal(
        (account.total_value or Decimal("0.00")) + normalized_delta
    )
    if next_total < Decimal("0.00"):
        raise HTTPException(status_code=400, detail="Saldo insuficiente na conta")

    account.total_value = next_total
    db.add(
        BankAccountTransaction(
            user_id=user_id,
            account_id=account.id,
            transfer_id=transfer_id,
            amount=normalized_delta,
            transaction_type=transaction_type,
            description=description,
        )
    )
    db.flush()
    return True
