from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from database import Base
from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class InvestmentPriceHistory(Base):
    __tablename__ = "investment_price_history"
    __table_args__ = (
        Index(
            "ix_investment_price_history_investment_captured_at",
            "investment_id",
            "captured_at",
        ),
        Index(
            "ix_investment_price_history_user_ticker_captured_at",
            "user_id",
            "ticker",
            "captured_at",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    investment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("investments.id", ondelete="CASCADE"), nullable=False
    )
    ticker: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="BRL"
    )
    source: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="brapi"
    )
    captured_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    investment: Mapped["Investment"] = relationship(
        "Investment", back_populates="price_history"
    )
    user: Mapped["User"] = relationship("User")


from models.investment import Investment  # noqa: E402,F401
from models.user import User  # noqa: E402,F401
