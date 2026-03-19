from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List

from database import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PatrimonySnapshot(Base):
    __tablename__ = "patrimony_snapshots"
    __table_args__ = (
        Index("ix_patrimony_snapshots_user_snapshot_at", "user_id", "snapshot_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    total_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    has_breakdown: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0", default=False
    )
    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    user: Mapped["User"] = relationship("User", back_populates="patrimony_snapshots")
    accounts: Mapped[List["PatrimonySnapshotAccount"]] = relationship(
        "PatrimonySnapshotAccount",
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )


from models.patrimony_snapshot_account import (  # noqa: E402,F401
    PatrimonySnapshotAccount,
)
from models.user import User  # noqa: E402,F401
