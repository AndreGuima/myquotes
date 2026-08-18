from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from database import Base
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Dream(Base):
    __tablename__ = "dreams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    smart_target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    smart_financial_target_value: Mapped[Optional[float]] = mapped_column(
        Numeric(14, 2), nullable=True
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    user: Mapped["User"] = relationship("User", back_populates="dreams")
    milestones: Mapped[List["DreamMilestone"]] = relationship(
        "DreamMilestone",
        back_populates="dream",
        cascade="all, delete-orphan",
        order_by="DreamMilestone.position",
    )
    habit_links: Mapped[List["DreamHabitLink"]] = relationship(
        "DreamHabitLink",
        back_populates="dream",
        cascade="all, delete-orphan",
    )
    bank_accounts: Mapped[List["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="objective_dream",
    )


class DreamMilestone(Base):
    __tablename__ = "dream_milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dream_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dreams.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    financial_target_value: Mapped[Optional[float]] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    progress_percent: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, server_default="0"
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    dream: Mapped["Dream"] = relationship("Dream", back_populates="milestones")


class DreamHabitLink(Base):
    __tablename__ = "dream_habit_links"

    dream_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dreams.id", ondelete="CASCADE"), primary_key=True
    )
    habit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("habits.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    dream: Mapped["Dream"] = relationship("Dream", back_populates="habit_links")
    habit: Mapped["Habit"] = relationship("Habit")


from models.bank_account import BankAccount  # noqa: E402,F401
from models.habit import Habit  # noqa: E402,F401
from models.user import User  # noqa: E402,F401
