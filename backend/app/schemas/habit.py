from datetime import time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator
from schemas.habit_stats import HabitStatsResponse


class FrequencyType(str, Enum):
    daily = "daily"
    weekly = "weekly"


class HabitCreate(BaseModel):
    title: str
    frequency_type: FrequencyType = FrequencyType.daily
    target_per_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @model_validator(mode="after")
    def validate_weekly_target(self):
        if self.frequency_type == FrequencyType.weekly and not self.target_per_week:
            raise ValueError("target_per_week is required for weekly habits")
        if self.start_time is None and self.end_time is not None:
            raise ValueError("start_time is required when end_time is set")
        if self.start_time is not None and self.end_time is not None:
            if self.end_time < self.start_time:
                raise ValueError("end_time must be after start_time")
        return self


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time is None and self.end_time is not None:
            raise ValueError("start_time is required when end_time is set")
        if self.start_time is not None and self.end_time is not None:
            if self.end_time < self.start_time:
                raise ValueError("end_time must be after start_time")
        return self


class HabitResponse(BaseModel):
    id: int
    title: str
    frequency_type: FrequencyType
    target_per_week: Optional[int]
    is_active: bool
    start_time: Optional[time]
    end_time: Optional[time]
    stats: Optional[HabitStatsResponse] = None

    model_config = ConfigDict(from_attributes=True)
