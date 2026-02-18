from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from database import Base
from sqlalchemy import TIMESTAMP, Boolean, Integer, String, func
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

    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    quotes: Mapped[List["Quote"]] = relationship(
        "Quote", back_populates="user", cascade="all, delete-orphan"
    )

    reading_list_books: Mapped[List["ReadingListBook"]] = relationship(
        "ReadingListBook", back_populates="user", cascade="all, delete-orphan"
    )
    dreams: Mapped[List["Dream"]] = relationship(
        "Dream", back_populates="user", cascade="all, delete-orphan"
    )
    bank_accounts: Mapped[List["BankAccount"]] = relationship(
        "BankAccount", back_populates="user", cascade="all, delete-orphan"
    )


from models.bank_account import BankAccount  # noqa: E402,F401
from models.dream import Dream  # noqa: E402,F401
from models.quote import Quote  # noqa: E402,F401
from models.reading_list_book import ReadingListBook  # noqa: E402,F401
