from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from database import Base
from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class IncomeTypeEnum(str, enum.Enum):
    dividend = "dividend"
    jcp = "jcp"
    rendimento = "rendimento"


class InvestmentIncome(Base):
    __tablename__ = "investment_incomes"
    __table_args__ = (
        Index(
            "ix_investment_incomes_user_received_date_id",
            "user_id",
            "received_at",
            "id",
        ),
        Index(
            "ix_investment_incomes_user_bank_account_id",
            "user_id",
            "bank_account_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    income_type: Mapped[IncomeTypeEnum] = mapped_column(
        Enum(
            IncomeTypeEnum,
            name="income_type_enum",
            native_enum=True,
            create_constraint=False,
        ),
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(String(30), nullable=False)
    bank_account_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("bank_accounts.id", ondelete="SET NULL"), nullable=True
    )
    received_at: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        server_default="",
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    user: Mapped["User"] = relationship("User", back_populates="investment_incomes")
    bank_account: Mapped["BankAccount | None"] = relationship("BankAccount")


from models.bank_account import BankAccount  # noqa: E402,F401
from models.user import User  # noqa: E402,F401
