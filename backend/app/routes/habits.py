from datetime import date

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.habit import Habit
from models.user import User
from schemas.habit import HabitCreate, HabitResponse, HabitUpdate
from schemas.habit_stats import HabitStatsResponse
from schemas.habit_toggle import HabitToggleResponse
from services.habit_log_service import HabitLogService
from services.habit_service import HabitService
from services.habit_stats_service import HabitStatsService
from sqlalchemy.orm import Session

router = APIRouter()


# =========================
# ➕ Criar hábito
# =========================
@router.post("", response_model=HabitResponse)
def create_habit(
    data: HabitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return HabitService.create(db, user.id, data)


# =========================
# 📋 Listar hábitos ativos
# =========================
@router.get("", response_model=list[HabitResponse])
def list_habits(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return HabitService.list_active(db, user.id)


# =========================
# ✏️ Atualizar hábito
# =========================
@router.put("/{habit_id}", response_model=HabitResponse)
@router.patch("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    habit = (
        db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if habit_update.title is not None:
        habit.title = habit_update.title

    if habit_update.is_active is not None:
        habit.is_active = habit_update.is_active

    db.commit()
    db.refresh(habit)
    return habit


# =========================
# ❌ Desativar hábito
# =========================
@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    habit = (
        db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    habit.is_active = False
    db.commit()


# =========================
# 📊 Estatísticas do hábito
# =========================
@router.get("/{habit_id}/stats", response_model=HabitStatsResponse)
def get_habit_stats(
    habit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
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


# =========================
# 🔁 Toggle diário
# =========================
@router.post("/{habit_id}/toggle", response_model=HabitToggleResponse)
def toggle_habit_today(
    habit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
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

        return {"log": log, "stats": stats}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
