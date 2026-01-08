from datetime import date

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.habit import Habit
from schemas.habit import HabitCreate, HabitResponse, HabitUpdate
from schemas.habit_stats import HabitStatsResponse
from schemas.habit_toggle import HabitToggleResponse
from services.habit_log_service import HabitLogService
from services.habit_service import HabitService
from services.habit_stats_service import HabitStatsService
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=HabitResponse)
def create_habit(
    data: HabitCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return HabitService.create(db, user.id, data)


@router.get("/", response_model=list[HabitResponse])
def list_habits(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return HabitService.list_active(db, user.id)


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    data: HabitUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    habit = (
        db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    return HabitService.update(db, habit, data)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    habit = (
        db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    HabitService.update(db, habit, HabitUpdate(is_active=False))
    return None


@router.get("/{habit_id}/stats", response_model=HabitStatsResponse)
def get_habit_stats(
    habit_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return HabitStatsService.get_stats(
            db,
            user_id=user.id,
            habit_id=habit_id,
            today=date.today(),
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Habit not found")


@router.post(
    "/{habit_id}/toggle",
    response_model=HabitToggleResponse,
)
def toggle_habit_today(
    habit_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        log = HabitLogService.toggle_today(
            db,
            user_id=user.id,
            habit_id=habit_id,
        )

        stats = HabitStatsService.get_stats(
            db,
            user_id=user.id,
            habit_id=habit_id,
        )

        return {
            "log": log,
            "stats": stats,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
