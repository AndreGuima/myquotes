import enum

from database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.sql import func


class FrequencyType(enum.Enum):
    daily = "daily"
    weekly = "weekly"


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)

    frequency_type = Column(
        Enum(
            FrequencyType,
            name="frequency_type_enum",
        ),
        nullable=False,
        default=FrequencyType.daily,
    )

    target_per_week = Column(Integer, nullable=True)
    weekdays = Column(JSON, nullable=True)

    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
