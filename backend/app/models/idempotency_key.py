from __future__ import annotations

from datetime import datetime

from database import Base
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        Index(
            "ux_idempotency_keys_user_route_key",
            "user_id",
            "route_key",
            "idempotency_key",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    route_key: Mapped[str] = mapped_column(String(120), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    user: Mapped["User"] = relationship("User", back_populates="idempotency_keys")


from models.user import User  # noqa: E402,F401
