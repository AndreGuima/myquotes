from pydantic import BaseModel
from schemas.habit_log import HabitLogResponse
from schemas.habit_stats import HabitStatsResponse


class HabitToggleResponse(BaseModel):
    log: HabitLogResponse
    stats: HabitStatsResponse
