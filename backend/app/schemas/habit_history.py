from datetime import date
from typing import List

from pydantic import BaseModel


class HabitHistoryDay(BaseModel):
    date: date
    completed: bool


class HabitHistoryResponse(BaseModel):
    habit_id: int
    from_date: date
    to_date: date
    days: List[HabitHistoryDay]
