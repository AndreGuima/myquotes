from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.bank_account import BankAccount
    from models.bank_account_transaction import BankAccountTransaction
    from models.user import User


class BankAccountTransfer(Base):
    __tablename__ = "bank_account_transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    from_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False
    )
    to_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    user: Mapped["User"] = relationship("User", back_populates="bank_account_transfers")
    from_account: Mapped["BankAccount"] = relationship(
        "BankAccount",
        back_populates="outgoing_transfers",
        foreign_keys=[from_account_id],
    )
    to_account: Mapped["BankAccount"] = relationship(
        "BankAccount",
        back_populates="incoming_transfers",
        foreign_keys=[to_account_id],
    )
    transactions: Mapped[list["BankAccountTransaction"]] = relationship(
        "BankAccountTransaction",
        back_populates="transfer",
    )
