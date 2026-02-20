from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from database import Base
from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        Index("ix_expenses_user_launch_date_id", "user_id", "launch_date", "id"),
        Index("ix_expenses_user_expense_category_id", "user_id", "expense_category_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    expense_category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("expense_categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    payment_method: Mapped[str] = mapped_column(String(10), nullable=False)
    bank_account_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("bank_accounts.id", ondelete="SET NULL"), nullable=True
    )
    credit_card_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("credit_cards.id", ondelete="SET NULL"), nullable=True
    )
    launch_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    user: Mapped["User"] = relationship("User", back_populates="expenses")
    bank_account: Mapped["BankAccount | None"] = relationship("BankAccount")
    credit_card: Mapped["CreditCard | None"] = relationship(
        "CreditCard", back_populates="expenses"
    )
    expense_category: Mapped["ExpenseCategory"] = relationship(
        "ExpenseCategory", back_populates="expenses"
    )


from models.bank_account import BankAccount  # noqa: E402,F401
from models.credit_card import CreditCard  # noqa: E402,F401
from models.expense_category import ExpenseCategory  # noqa: E402,F401
from models.user import User  # noqa: E402,F401
