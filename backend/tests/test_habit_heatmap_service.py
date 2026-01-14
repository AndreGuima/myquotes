from datetime import date, timedelta

import pytest
from models.habit import Habit
from models.habit_log import HabitLog
from services.habit_history_service import HabitHistoryService


def create_habit(db, *, user_id=1):
    habit = Habit(
        user_id=user_id,
        title="Heatmap Habit",
        frequency_type="daily",
        is_active=True,
    )
    db.add(habit)
    db.flush()
    db.refresh(habit)
    return habit


def create_log(db, habit_id, user_id, log_date):
    db.add(
        HabitLog(
            habit_id=habit_id,
            user_id=user_id,
            date=log_date,
            completed=True,
        )
    )
    db.flush()


def test_heatmap_returns_full_range(db_session):
    habit = create_habit(db_session)

    today = date.today()

    create_log(db_session, habit.id, 1, today)
    create_log(db_session, habit.id, 1, today - timedelta(days=2))

    result = HabitHistoryService.get_heatmap(
        db_session,
        user_id=1,
        habit_id=habit.id,
        days=5,
    )

    assert result["habit_id"] == habit.id
    assert len(result["days"]) == 5

    # deve conter todos os dias, inclusive os sem log
    counts = [d["count"] for d in result["days"]]
    assert 0 in counts
    assert 1 in counts


def test_heatmap_count_is_binary_per_day(db_session):
    habit = create_habit(db_session)
    today = date.today()

    # cria log (1 vez)
    create_log(db_session, habit.id, 1, today)

    result = HabitHistoryService.get_heatmap(
        db_session,
        user_id=1,
        habit_id=habit.id,
        days=1,
    )

    assert result["days"][0]["count"] == 1


def test_heatmap_inactive_habit_raises(db_session):
    habit = create_habit(db_session)
    habit.is_active = False
    db_session.commit()

    with pytest.raises(ValueError):
        HabitHistoryService.get_heatmap(
            db_session,
            user_id=1,
            habit_id=habit.id,
            days=7,
        )
