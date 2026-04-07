from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from database import Base
from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.bank_account import BankAccount
    from models.bank_account_transfer import BankAccountTransfer
    from models.user import User


class TransactionType(str, Enum):
    OPENING_BALANCE = "opening_balance"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    TRANSFER = "transfer"
    EXPENSE = "expense"
    EXPENSE_ADJUSTMENT = "expense_adjustment"
    EXPENSE_REVERSAL = "expense_reversal"
    INVOICE_PAYMENT = "invoice_payment"
    INVESTMENT_INCOME = "investment_income"
    INVESTMENT_INCOME_ADJUSTMENT = "investment_income_adjustment"
    INVESTMENT_INCOME_REVERSAL = "investment_income_reversal"


class BankAccountTransaction(Base):
    __tablename__ = "bank_account_transactions"
    __table_args__ = (
        Index("idx_bat_account_id", "account_id"),
        Index("idx_bat_user_id", "user_id"),
        Index("idx_bat_transfer_id", "transfer_id"),
        Index("idx_bat_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False
    )
    transfer_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("bank_account_transfers.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, name="bank_account_transaction_type"),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="bank_account_transactions"
    )
    account: Mapped["BankAccount"] = relationship(
        "BankAccount", back_populates="transactions"
    )
    transfer: Mapped["BankAccountTransfer | None"] = relationship(
        "BankAccountTransfer", back_populates="transactions"
    )
