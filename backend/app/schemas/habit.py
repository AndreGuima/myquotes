from datetime import time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from schemas.habit_stats import HabitStatsResponse


class FrequencyType(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class HabitCreate(BaseModel):
    title: str
    description: Optional[str] = Field(default=None, max_length=1000)
    frequency_type: FrequencyType = FrequencyType.daily
    target_per_week: Optional[int] = None
    weekdays: Optional[list[int]] = None
    month_day: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @model_validator(mode="after")
    def validate_weekly_target(self):
        if self.frequency_type == FrequencyType.weekly and not self.weekdays:
            raise ValueError("weekdays is required for weekly habits")
        if self.frequency_type != FrequencyType.weekly and self.weekdays:
            raise ValueError("weekdays is only allowed for weekly habits")
        if self.frequency_type == FrequencyType.monthly and self.month_day is None:
            raise ValueError("month_day is required for monthly habits")
        if self.frequency_type != FrequencyType.monthly and self.month_day is not None:
            raise ValueError("month_day is only allowed for monthly habits")
        if self.weekdays is not None:
            if any((day < 0 or day > 6) for day in self.weekdays):
                raise ValueError("weekdays must be between 0 and 6")
            if len(set(self.weekdays)) != len(self.weekdays):
                raise ValueError("weekdays must not contain duplicates")
        if self.month_day is not None and (self.month_day < 1 or self.month_day > 31):
            raise ValueError("month_day must be between 1 and 31")
        if self.start_time is None and self.end_time is not None:
            raise ValueError("start_time is required when end_time is set")
        return self


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=1000)
    is_active: Optional[bool] = None
    weekdays: Optional[list[int]] = None
    month_day: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.weekdays is not None:
            if any((day < 0 or day > 6) for day in self.weekdays):
                raise ValueError("weekdays must be between 0 and 6")
            if len(set(self.weekdays)) != len(self.weekdays):
                raise ValueError("weekdays must not contain duplicates")
        if self.month_day is not None and (self.month_day < 1 or self.month_day > 31):
            raise ValueError("month_day must be between 1 and 31")
        if self.weekdays is not None and self.month_day is not None:
            raise ValueError("weekdays and month_day cannot be sent together")
        if self.start_time is None and self.end_time is not None:
            raise ValueError("start_time is required when end_time is set")
        return self


class HabitResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    frequency_type: FrequencyType
    target_per_week: Optional[int]
    weekdays: Optional[list[int]]
    month_day: Optional[int]
    is_active: bool
    start_time: Optional[time]
    end_time: Optional[time]
    stats: Optional[HabitStatsResponse] = None

    model_config = ConfigDict(from_attributes=True)
