from datetime import date, timedelta

from models.habit import FrequencyType, Habit
from models.habit_log import HabitLog
from sqlalchemy.orm import Session


class HabitStatsService:
    @staticmethod
    def get_stats(
        db: Session,
        *,
        user_id: int,
        habit_id: int,
        today: date | None = None,
    ) -> dict:
        if today is None:
            today = date.today()

        # -------------------------------------------------
        # 1️⃣ Valida hábito
        # -------------------------------------------------
        habit = (
            db.query(Habit)
            .filter(
                Habit.id == habit_id,
                Habit.user_id == user_id,
            )
            .first()
        )

        if not habit:
            raise ValueError("Habit not found")

        # -------------------------------------------------
        # 2️⃣ Carrega logs (ordenados)
        # -------------------------------------------------
        logs = (
            db.query(HabitLog)
            .filter(
                HabitLog.habit_id == habit_id,
                HabitLog.user_id == user_id,
                HabitLog.completed.is_(True),
            )
            .order_by(HabitLog.date.desc())
            .all()
        )

        log_dates = {log.date for log in logs}

        # -------------------------------------------------
        # 3️⃣ Status de hoje
        # -------------------------------------------------
        today_completed = today in log_dates

        # -------------------------------------------------
        # 4️⃣ Current streak
        # -------------------------------------------------
        current_streak = 0
        cursor = today

        while cursor in log_dates:
            current_streak += 1
            cursor -= timedelta(days=1)

        # -------------------------------------------------
        # 5️⃣ Best streak (histórico)
        # -------------------------------------------------
        best_streak = 0
        streak = 0
        previous_day = None

        for log_date in sorted(log_dates):
            if previous_day is None or log_date != previous_day + timedelta(days=1):
                streak = 1
            else:
                streak += 1

            best_streak = max(best_streak, streak)
            previous_day = log_date

        # -------------------------------------------------
        # 6️⃣ Progresso semanal
        # -------------------------------------------------
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        weekly_completed = sum(1 for d in log_dates if week_start <= d <= week_end)

        weekly_target = (
            habit.target_per_week
            if habit.frequency_type == FrequencyType.weekly
            else None
        )

        # -------------------------------------------------
        # 7️⃣ Resultado final
        # -------------------------------------------------
        return {
            "today_completed": today_completed,
            "current_streak": current_streak,
            "best_streak": best_streak,
            "weekly_completed": weekly_completed,
            "weekly_target": weekly_target,
        }
