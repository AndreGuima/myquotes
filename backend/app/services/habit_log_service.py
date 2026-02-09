from datetime import datetime

from models.habit import Habit
from models.habit_log import HabitLog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class HabitLogService:
    @staticmethod
    def toggle_today(
        db: Session,
        *,
        user_id: int,
        habit_id: int,
        now_dt: datetime | None = None,
    ) -> HabitLog:
        now = now_dt or datetime.now()
        today = now.date()

        # -------------------------------------------------
        # 1️⃣ Valida hábito (sem lock)
        # -------------------------------------------------
        habit = db.query(Habit).filter(Habit.id == habit_id).first()

        if not habit:
            raise ValueError("Habit not found")

        if habit.user_id != user_id:
            raise ValueError("Habit does not belong to user")

        if not habit.is_active:
            raise ValueError("Habit is inactive")

        if habit.start_time:
            now_time = now.time()
            is_overnight = bool(habit.end_time and habit.end_time < habit.start_time)
            # Overnight habits (e.g. 22:00-06:00) can be checked in the morning/day
            # after finishing the routine.
            if not is_overnight:
                if now_time < habit.start_time:
                    raise ValueError("Habit is before scheduled time")

        # -------------------------------------------------
        # 2️⃣ Busca log do dia COM LOCK
        # -------------------------------------------------
        log = (
            db.query(HabitLog)
            .filter(
                HabitLog.habit_id == habit_id,
                HabitLog.date == today,
            )
            .with_for_update()
            .first()
        )

        # -------------------------------------------------
        # 3️⃣ Toggle ou cria
        # -------------------------------------------------
        if log:
            log.completed = not log.completed
        else:
            log = HabitLog(
                habit_id=habit_id,
                user_id=user_id,
                date=today,
                completed=True,
            )
            db.add(log)

        try:
            db.commit()
        except IntegrityError:
            # 🔒 fallback defensivo (concorrência extrema)
            db.rollback()
            log = (
                db.query(HabitLog)
                .filter(
                    HabitLog.habit_id == habit_id,
                    HabitLog.date == today,
                )
                .first()
            )
            if not log:
                raise

        db.refresh(log)
        return log
