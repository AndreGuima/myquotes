from datetime import date, timedelta

from models.habit import Habit
from models.habit_log import HabitLog
from sqlalchemy import func
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

    # 🔥 NOVO MÉTODO PARA HEATMAP
    @staticmethod
    def get_heatmap(
        db: Session,
        *,
        user_id: int,
        habit_id: int,
        days: int = 90,
    ):
        to_date = date.today()
        from_date = to_date - timedelta(days=days - 1)

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

        # Agrupa por data e conta logs
        results = (
            db.query(
                HabitLog.date,
                func.count(HabitLog.id).label("count"),
            )
            .filter(
                HabitLog.habit_id == habit_id,
                HabitLog.user_id == user_id,
                HabitLog.date >= from_date,
                HabitLog.date <= to_date,
            )
            .group_by(HabitLog.date)
            .all()
        )

        count_map = {row.date: row.count for row in results}

        days_data = []
        current = from_date
        while current <= to_date:
            days_data.append(
                {
                    "date": current.isoformat(),
                    "count": count_map.get(current, 0),
                }
            )
            current += timedelta(days=1)

        return {
            "habit_id": habit_id,
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            "days": days_data,
        }
