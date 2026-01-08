from datetime import date, timedelta

import pytest
from models.habit import Habit
from models.habit_log import HabitLog

# ⚠️ ainda não existe → TDD
from services.habit_stats_service import HabitStatsService


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def create_habit(db, *, user_id: int, frequency="daily", target=None):
    habit = Habit(
        user_id=user_id,
        title="Hábito Teste",
        frequency_type=frequency,
        target_per_week=target,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def create_log(db, *, habit_id, user_id, log_date, completed=True):
    log = HabitLog(
        habit_id=habit_id,
        user_id=user_id,
        date=log_date,
        completed=completed,
    )
    db.add(log)
    db.commit()
    return log


# -------------------------------------------------
# Tests
# -------------------------------------------------
def test_today_not_completed_when_no_log(db_session):
    habit = create_habit(db_session, user_id=1)

    stats = HabitStatsService.get_stats(
        db_session,
        user_id=1,
        habit_id=habit.id,
        today=date.today(),
    )

    assert stats["today_completed"] is False
    assert stats["current_streak"] == 0
    assert stats["best_streak"] == 0


def test_today_completed_when_log_exists(db_session):
    habit = create_habit(db_session, user_id=1)
    today = date.today()

    create_log(
        db_session,
        habit_id=habit.id,
        user_id=1,
        log_date=today,
        completed=True,
    )

    stats = HabitStatsService.get_stats(
        db_session,
        user_id=1,
        habit_id=habit.id,
        today=today,
    )

    assert stats["today_completed"] is True
    assert stats["current_streak"] == 1
    assert stats["best_streak"] == 1


def test_streak_counts_consecutive_days(db_session):
    habit = create_habit(db_session, user_id=1)
    today = date.today()

    for i in range(3):
        create_log(
            db_session,
            habit_id=habit.id,
            user_id=1,
            log_date=today - timedelta(days=i),
            completed=True,
        )

    stats = HabitStatsService.get_stats(
        db_session,
        user_id=1,
        habit_id=habit.id,
        today=today,
    )

    assert stats["current_streak"] == 3
    assert stats["best_streak"] == 3


def test_streak_breaks_on_missing_day(db_session):
    habit = create_habit(db_session, user_id=1)
    today = date.today()

    create_log(db_session, habit_id=habit.id, user_id=1, log_date=today)
    create_log(
        db_session,
        habit_id=habit.id,
        user_id=1,
        log_date=today - timedelta(days=2),
    )

    stats = HabitStatsService.get_stats(
        db_session,
        user_id=1,
        habit_id=habit.id,
        today=today,
    )

    assert stats["current_streak"] == 1
    assert stats["best_streak"] == 1


def test_best_streak_persists_after_break(db_session):
    habit = create_habit(db_session, user_id=1)
    today = date.today()

    # streak antigo de 3
    for i in range(5, 2, -1):
        create_log(
            db_session,
            habit_id=habit.id,
            user_id=1,
            log_date=today - timedelta(days=i),
        )

    # streak atual de 2
    create_log(db_session, habit_id=habit.id, user_id=1, log_date=today)
    create_log(
        db_session,
        habit_id=habit.id,
        user_id=1,
        log_date=today - timedelta(days=1),
    )

    stats = HabitStatsService.get_stats(
        db_session,
        user_id=1,
        habit_id=habit.id,
        today=today,
    )

    assert stats["current_streak"] == 2
    assert stats["best_streak"] == 3


def test_weekly_progress_daily_habit(db_session):
    habit = create_habit(db_session, user_id=1, frequency="daily")
    today = date.today()

    create_log(db_session, habit_id=habit.id, user_id=1, log_date=today)
    create_log(
        db_session,
        habit_id=habit.id,
        user_id=1,
        log_date=today - timedelta(days=1),
    )

    stats = HabitStatsService.get_stats(
        db_session,
        user_id=1,
        habit_id=habit.id,
        today=today,
    )

    assert stats["weekly_completed"] == 2
    assert stats["weekly_target"] is None


def test_weekly_progress_weekly_habit(db_session):
    habit = create_habit(
        db_session,
        user_id=1,
        frequency="weekly",
        target=3,
    )
    today = date.today()

    create_log(db_session, habit_id=habit.id, user_id=1, log_date=today)
    create_log(
        db_session,
        habit_id=habit.id,
        user_id=1,
        log_date=today - timedelta(days=2),
    )

    stats = HabitStatsService.get_stats(
        db_session,
        user_id=1,
        habit_id=habit.id,
        today=today,
    )

    assert stats["weekly_completed"] == 2
    assert stats["weekly_target"] == 3
