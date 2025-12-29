from __future__ import annotations

from datetime import datetime
from typing import Optional

from database import Base
from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="Desconhecido"
    )
    text: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    # 🔗 Relacionamento com User
    user: Mapped["User"] = relationship("User", back_populates="quotes")


# 👇 Import atrasado para evitar import circular
from models.user import User  # noqa: E402,F401
