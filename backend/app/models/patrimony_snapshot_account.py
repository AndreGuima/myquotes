from __future__ import annotations

from decimal import Decimal

from database import Base
from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PatrimonySnapshotAccount(Base):
    __tablename__ = "patrimony_snapshot_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patrimony_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bank_account_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    account_name: Mapped[str] = mapped_column(String(120), nullable=False)
    total_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    snapshot: Mapped["PatrimonySnapshot"] = relationship(
        "PatrimonySnapshot",
        back_populates="accounts",
    )


from models.patrimony_snapshot import PatrimonySnapshot  # noqa: E402,F401
