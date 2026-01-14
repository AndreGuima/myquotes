from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator


class FrequencyType(str, Enum):
    daily = "daily"
    weekly = "weekly"


class HabitCreate(BaseModel):
    title: str
    frequency_type: FrequencyType = FrequencyType.daily
    target_per_week: Optional[int] = None

    @model_validator(mode="after")
    def validate_weekly_target(self):
        if self.frequency_type == FrequencyType.weekly and not self.target_per_week:
            raise ValueError("target_per_week is required for weekly habits")
        return self


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None


class HabitResponse(BaseModel):
    id: int
    title: str
    frequency_type: FrequencyType
    target_per_week: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True
