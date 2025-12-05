from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import TIMESTAMP, Boolean, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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

    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    quotes: Mapped[List["Quote"]] = relationship(
        "Quote", back_populates="user", cascade="all, delete-orphan"
    )


# 👇 Import atrasado para resolver o F821 sem gerar loop
from app.models.quote import Quote  # noqa: E402,F401
