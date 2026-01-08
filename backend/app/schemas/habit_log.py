from datetime import date
from typing import Optional

from pydantic import BaseModel


class HabitLogBase(BaseModel):
    date: date
    completed: bool


class HabitLogCreate(BaseModel):
    """
    Usado apenas se no futuro quisermos criar logs manuais.
    Para o MVP, o check diário não precisa desse schema.
    """

    date: Optional[date] = None


class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    date: date
    completed: bool

    class Config:
        from_attributes = True
