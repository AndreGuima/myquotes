# backend/app/services/habit_service.py
from models.habit import Habit
from schemas.habit import HabitCreate, HabitUpdate
from sqlalchemy.orm import Session


class HabitService:
    @staticmethod
    def create(db: Session, user_id: int, data: HabitCreate):
        habit = Habit(
            user_id=user_id,
            title=data.title,
            frequency_type=data.frequency_type,
            target_per_week=data.target_per_week,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    @staticmethod
    def list_active(db: Session, user_id: int):
        return (
            db.query(Habit)
            .filter(Habit.user_id == user_id, Habit.is_active.is_(True))
            .all()
        )

    @staticmethod
    def list_active_with_stats(db: Session, user_id: int, *, stats_service):
        habits = HabitService.list_active(db, user_id)
        for habit in habits:
            habit.stats = stats_service.get_stats(
                db,
                user_id=user_id,
                habit_id=habit.id,
            )
        return habits

    @staticmethod
    def update(db: Session, habit: Habit, data: HabitUpdate):
        updates = data.dict(exclude_unset=True)

        # defesa extra (future-proof)
        updates.pop("user_id", None)

        for field, value in updates.items():
            setattr(habit, field, value)

        db.commit()
        db.refresh(habit)
        return habit
