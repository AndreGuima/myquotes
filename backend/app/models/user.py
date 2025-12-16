from __future__ import annotations

from datetime import datetime, time
from typing import List, Optional

from database import Base
from sqlalchemy import TIMESTAMP, Boolean, Integer, String, Time, func
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

    receive_daily_quote: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="1", default=True
    )

    # ✅ ESTA LINHA ESTAVA FALTANDO
    daily_quote_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    quotes: Mapped[List["Quote"]] = relationship(
        "Quote", back_populates="user", cascade="all, delete-orphan"
    )


from models.quote import Quote  # noqa: E402,F401
