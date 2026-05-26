from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from database import Base
from sqlalchemy import TIMESTAMP, Boolean, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")

    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0", default=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="1", default=True
    )

    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    quotes: Mapped[List["Quote"]] = relationship(
        "Quote", back_populates="user", cascade="all, delete-orphan"
    )

    reading_list_books: Mapped[List["ReadingListBook"]] = relationship(
        "ReadingListBook", back_populates="user", cascade="all, delete-orphan"
    )
    dreams: Mapped[List["Dream"]] = relationship(
        "Dream", back_populates="user", cascade="all, delete-orphan"
    )
    bank_accounts: Mapped[List["BankAccount"]] = relationship(
        "BankAccount", back_populates="user", cascade="all, delete-orphan"
    )
    bank_account_transactions: Mapped[List["BankAccountTransaction"]] = relationship(
        "BankAccountTransaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    bank_account_transfers: Mapped[List["BankAccountTransfer"]] = relationship(
        "BankAccountTransfer",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    idempotency_keys: Mapped[List["IdempotencyKey"]] = relationship(
        "IdempotencyKey",
        cascade="all, delete-orphan",
    )
    credit_cards: Mapped[List["CreditCard"]] = relationship(
        "CreditCard", back_populates="user", cascade="all, delete-orphan"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="user", cascade="all, delete-orphan"
    )
    investment_incomes: Mapped[List["InvestmentIncome"]] = relationship(
        "InvestmentIncome", back_populates="user", cascade="all, delete-orphan"
    )
    investments: Mapped[List["Investment"]] = relationship(
        "Investment", back_populates="user", cascade="all, delete-orphan"
    )
    expense_categories: Mapped[List["ExpenseCategory"]] = relationship(
        "ExpenseCategory", back_populates="user", cascade="all, delete-orphan"
    )
    patrimony_snapshots: Mapped[List["PatrimonySnapshot"]] = relationship(
        "PatrimonySnapshot", back_populates="user", cascade="all, delete-orphan"
    )
    notes: Mapped[List["Note"]] = relationship(
        "Note", back_populates="user", cascade="all, delete-orphan"
    )


from models.bank_account import BankAccount  # noqa: E402,F401
from models.bank_account_transaction import BankAccountTransaction  # noqa: E402,F401
from models.bank_account_transfer import BankAccountTransfer  # noqa: E402,F401
from models.credit_card import CreditCard  # noqa: E402,F401
from models.dream import Dream  # noqa: E402,F401
from models.expense import Expense  # noqa: E402,F401
from models.expense_category import ExpenseCategory  # noqa: E402,F401
from models.idempotency_key import IdempotencyKey  # noqa: E402,F401
from models.investment import Investment  # noqa: E402,F401
from models.investment_income import InvestmentIncome  # noqa: E402,F401
from models.note import Note  # noqa: E402,F401
from models.patrimony_snapshot import PatrimonySnapshot  # noqa: E402,F401
from models.patrimony_snapshot_account import (  # noqa: E402,F401
    PatrimonySnapshotAccount,
)
from models.quote import Quote  # noqa: E402,F401
from models.reading_list_book import ReadingListBook  # noqa: E402,F401
