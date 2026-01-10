from datetime import date, timedelta

from models.habit import Habit
from models.habit_log import HabitLog
from sqlalchemy.orm import Session


class HabitHistoryService:
    @staticmethod
    def get_history(
        db: Session,
        *,
        user_id: int,
        habit_id: int,
        from_date: date,
        to_date: date,
    ):
        habit = (
            db.query(Habit)
            .filter(
                Habit.id == habit_id,
                Habit.user_id == user_id,
                Habit.is_active.is_(True),
            )
            .first()
        )

        if not habit:
            raise ValueError("Habit not found")

        logs = (
            db.query(HabitLog)
            .filter(
                HabitLog.habit_id == habit_id,
                HabitLog.user_id == user_id,
                HabitLog.date >= from_date,
                HabitLog.date <= to_date,
            )
            .all()
        )

        log_map = {log.date: log.completed for log in logs}

        days = []
        current = from_date
        while current <= to_date:
            days.append(
                {
                    "date": current,
                    "completed": log_map.get(current, False),
                }
            )
            current += timedelta(days=1)

        return days
