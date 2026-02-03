from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ReadingStatus(str):
    TO_READ = "to_read"
    READING = "reading"
    READ = "read"


class ReadingListBook(Base):
    __tablename__ = "reading_list_books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ReadingStatus.TO_READ
    )
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    user: Mapped["User"] = relationship("User", back_populates="reading_list_books")
    logs: Mapped[List["ReadingListLog"]] = relationship(
        "ReadingListLog", back_populates="book", cascade="all, delete-orphan"
    )


from models.reading_list_log import ReadingListLog  # noqa: E402,F401
from models.user import User  # noqa: E402,F401
