from __future__ import annotations

from datetime import date, datetime

from database import Base
from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ReadingListLog(Base):
    __tablename__ = "reading_list_logs"
    __table_args__ = (
        UniqueConstraint("book_id", "log_date", name="uq_reading_log_book_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reading_list_books.id", ondelete="CASCADE"), nullable=False
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    comment: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    book: Mapped["ReadingListBook"] = relationship(
        "ReadingListBook", back_populates="logs"
    )


from models.reading_list_book import ReadingListBook  # noqa: E402,F401
