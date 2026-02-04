from datetime import date, timedelta

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.habit import Habit
from models.user import User
from schemas.habit import HabitCreate, HabitResponse, HabitUpdate
from schemas.habit_history import HabitHistoryResponse
from schemas.habit_stats import HabitStatsResponse
from schemas.habit_toggle import HabitToggleResponse
from services.habit_history_service import HabitHistoryService
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
    include_stats: bool = False,
):
    if include_stats:
        return HabitService.list_active_with_stats(
            db,
            user.id,
            stats_service=HabitStatsService,
        )
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

    return HabitService.update(db, habit, habit_update)


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
        detail = str(e)
        status_code = (
            status.HTTP_403_FORBIDDEN
            if detail == "Habit is before scheduled time"
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=detail)


# =========================
# 📅 Histórico do hábito
# =========================
@router.get(
    "/{habit_id}/history",
    response_model=HabitHistoryResponse,
)
def get_habit_history(
    habit_id: int,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if to_date is None:
        to_date = date.today()

    if from_date is None:
        from_date = to_date - timedelta(days=29)

    try:
        days = HabitHistoryService.get_history(
            db,
            user_id=user.id,
            habit_id=habit_id,
            from_date=from_date,
            to_date=to_date,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Habit not found")

    return {
        "habit_id": habit_id,
        "from_date": from_date,
        "to_date": to_date,
        "days": days,
    }


# =========================
# 🔥 Heatmap do hábito
# =========================
@router.get("/{habit_id}/heatmap")
def get_habit_heatmap(
    habit_id: int,
    days: int = 90,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if days < 7 or days > 365:
        raise HTTPException(
            status_code=400,
            detail="days must be between 7 and 365",
        )

    try:
        return HabitHistoryService.get_heatmap(
            db,
            user_id=user.id,
            habit_id=habit_id,
            days=days,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Habit not found")
