from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from database import Base
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class InvestmentAssetTypeEnum(str, enum.Enum):
    stock = "stock"
    fii = "fii"


class Investment(Base):
    __tablename__ = "investments"
    __table_args__ = (
        Index("ix_investments_user_ticker", "user_id", "ticker"),
        Index("ix_investments_user_asset_type", "user_id", "asset_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    asset_type: Mapped[InvestmentAssetTypeEnum] = mapped_column(
        Enum(
            InvestmentAssetTypeEnum,
            name="investment_asset_type_enum",
            native_enum=True,
            create_constraint=False,
        ),
        nullable=False,
    )
    sector: Mapped[str] = mapped_column(String(120), nullable=False, server_default="")
    ticker: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    average_price: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    current_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    price_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    user: Mapped["User"] = relationship("User", back_populates="investments")
    price_history: Mapped[list["InvestmentPriceHistory"]] = relationship(
        "InvestmentPriceHistory",
        back_populates="investment",
        cascade="all, delete-orphan",
        order_by="InvestmentPriceHistory.captured_at.desc()",
    )


from models.investment_price_history import InvestmentPriceHistory  # noqa: E402,F401
from models.user import User  # noqa: E402,F401
