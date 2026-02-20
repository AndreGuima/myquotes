from __future__ import annotations

from datetime import datetime

from database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CreditCard(Base):
    __tablename__ = "credit_cards"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="ux_credit_cards_user_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    user: Mapped["User"] = relationship("User", back_populates="credit_cards")
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates="credit_card"
    )


from models.expense import Expense  # noqa: E402,F401
from models.user import User  # noqa: E402,F401
