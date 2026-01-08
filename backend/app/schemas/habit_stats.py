from typing import Optional

from pydantic import BaseModel


class HabitStatsResponse(BaseModel):
    today_completed: bool
    current_streak: int
    best_streak: int
    weekly_completed: int
    weekly_target: Optional[int]
