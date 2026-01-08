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
    def update(db: Session, habit: Habit, data: HabitUpdate):
        updates = data.dict(exclude_unset=True)

        # defesa extra (future-proof)
        updates.pop("user_id", None)

        for field, value in updates.items():
            setattr(habit, field, value)

        db.commit()
        db.refresh(habit)
        return habit
