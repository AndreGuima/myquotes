from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PatrimonySnapshot(Base):
    __tablename__ = "patrimony_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    total_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    user: Mapped["User"] = relationship("User", back_populates="patrimony_snapshots")


from models.user import User  # noqa: E402,F401
