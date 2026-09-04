from datetime import datetime, timezone

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.dream import Dream, DreamHabitLink, DreamMilestone
from models.habit import Habit
from models.user import User
from schemas.dream import (
    DreamCreate,
    DreamMilestoneProgressPayload,
    DreamMilestoneRead,
    DreamMilestoneToggleRead,
    DreamRead,
    DreamSmartPayload,
    DreamSmartRead,
    DreamUpdate,
)
from services.dream_financial_progress import (
    get_dream_financial_progress,
    sync_dream_milestone_financial_progress,
)
from sqlalchemy.orm import Session, selectinload

router = APIRouter(prefix="/dreams", tags=["Dreams"])


def _to_response(db: Session, user_id: int, dream: Dream) -> DreamRead:
    linked_habit_ids = [link.habit_id for link in dream.habit_links]
    financial_progress = get_dream_financial_progress(db, user_id, dream)
    milestones = [
        DreamMilestoneRead(
            id=item.id,
            title=item.title,
            targetDate=item.target_date,
            completedAt=item.completed_at,
            financialTargetValue=item.financial_target_value,
            financialCurrentValue=item.financial_current_value,
            progressPercent=item.progress_percent,
            position=item.position,
        )
        for item in sorted(dream.milestones, key=lambda x: x.position)
    ]

    return DreamRead(
        id=dream.id,
        title=dream.title,
        description=dream.description,
        smart=DreamSmartRead(
            targetDate=dream.smart_target_date,
            financialTargetValue=dream.smart_financial_target_value,
            financialCurrentValue=financial_progress.total_amount,
            financialRemainingValue=financial_progress.remaining_amount,
            financialProgressPercent=financial_progress.progress_percent,
        ),
        linkedHabitIds=linked_habit_ids,
        milestones=milestones,
        createdAt=dream.created_at,
        updatedAt=dream.updated_at,
    )


def _validate_habits_belong_to_user(db: Session, user_id: int, habit_ids: list[int]):
    if not habit_ids:
        return
    count = (
        db.query(Habit)
        .filter(
            Habit.user_id == user_id, Habit.id.in_(habit_ids), Habit.is_active.is_(True)
        )
        .count()
    )
    if count != len(set(habit_ids)):
        raise HTTPException(
            status_code=400,
            detail="Hábitos inválidos para vincular ao sonho",
        )


def _apply_payload_to_dream(
    db: Session,
    dream: Dream,
    payload: DreamCreate | DreamUpdate,
    is_create: bool,
):
    if is_create or payload.title is not None:
        clean_title = payload.title.strip()
        if not clean_title:
            raise HTTPException(status_code=400, detail="Título do sonho é obrigatório")
        dream.title = clean_title

    if is_create or payload.description is not None:
        dream.description = payload.description.strip() if payload.description else None

    if is_create or payload.smart is not None:
        smart = payload.smart or DreamSmartPayload()
        dream.smart_target_date = smart.targetDate
        dream.smart_financial_target_value = smart.financialTargetValue

    if is_create or payload.linkedHabitIds is not None:
        linked_habits = list(dict.fromkeys(payload.linkedHabitIds or []))
        _validate_habits_belong_to_user(db, dream.user_id, linked_habits)
        dream.habit_links = [
            DreamHabitLink(habit_id=habit_id) for habit_id in linked_habits
        ]

    if is_create or payload.milestones is not None:
        milestone_payloads = payload.milestones or []
        dream.milestones = []
        for index, item in enumerate(milestone_payloads):
            clean_title = item.title.strip()
            if not clean_title:
                raise HTTPException(
                    status_code=400, detail="Título do marco é obrigatório"
                )
            dream.milestones.append(
                DreamMilestone(
                    title=clean_title,
                    target_date=item.targetDate,
                    completed_at=item.completedAt,
                    financial_target_value=item.financialTargetValue,
                    financial_current_value=item.financialCurrentValue,
                    progress_percent=item.progressPercent or 0,
                    position=index,
                )
            )


def _get_user_dream_or_404(db: Session, user_id: int, dream_id: int) -> Dream:
    dream = (
        db.query(Dream)
        .options(
            selectinload(Dream.milestones),
            selectinload(Dream.habit_links),
        )
        .filter(Dream.id == dream_id, Dream.user_id == user_id)
        .first()
    )
    if not dream:
        raise HTTPException(status_code=404, detail="Sonho não encontrado")
    return dream


@router.get("", response_model=list[DreamRead])
def list_dreams(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dreams = (
        db.query(Dream)
        .options(
            selectinload(Dream.milestones),
            selectinload(Dream.habit_links),
        )
        .filter(Dream.user_id == user.id)
        .order_by(Dream.created_at.desc())
        .all()
    )
    for dream in dreams:
        sync_dream_milestone_financial_progress(db, user.id, dream.id)
    db.commit()
    dreams = (
        db.query(Dream)
        .options(
            selectinload(Dream.milestones),
            selectinload(Dream.habit_links),
        )
        .filter(Dream.user_id == user.id)
        .order_by(Dream.created_at.desc())
        .all()
    )
    return [_to_response(db, user.id, dream) for dream in dreams]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DreamRead)
def create_dream(
    payload: DreamCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dream = Dream(user_id=user.id, title=payload.title.strip())
    _apply_payload_to_dream(db, dream, payload, is_create=True)

    db.add(dream)
    db.flush()
    sync_dream_milestone_financial_progress(db, user.id, dream.id)
    db.commit()
    db.refresh(dream)
    dream = _get_user_dream_or_404(db, user.id, dream.id)
    return _to_response(db, user.id, dream)


@router.get("/{dream_id}", response_model=DreamRead)
def get_dream(
    dream_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dream = _get_user_dream_or_404(db, user.id, dream_id)
    sync_dream_milestone_financial_progress(db, user.id, dream.id)
    db.commit()
    dream = _get_user_dream_or_404(db, user.id, dream_id)
    return _to_response(db, user.id, dream)


@router.patch("/{dream_id}", response_model=DreamRead)
def update_dream(
    dream_id: int,
    payload: DreamUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dream = _get_user_dream_or_404(db, user.id, dream_id)
    _apply_payload_to_dream(db, dream, payload, is_create=False)
    db.flush()
    sync_dream_milestone_financial_progress(db, user.id, dream.id)
    db.commit()
    db.refresh(dream)
    dream = _get_user_dream_or_404(db, user.id, dream.id)
    return _to_response(db, user.id, dream)


@router.delete("/{dream_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dream(
    dream_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dream = _get_user_dream_or_404(db, user.id, dream_id)
    db.delete(dream)
    db.commit()
    return None


@router.post(
    "/{dream_id}/milestones/{milestone_id}/toggle",
    response_model=DreamMilestoneToggleRead,
)
def toggle_milestone(
    dream_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dream = _get_user_dream_or_404(db, user.id, dream_id)

    milestone = next(
        (item for item in dream.milestones if item.id == milestone_id), None
    )
    if not milestone:
        raise HTTPException(status_code=404, detail="Marco não encontrado")

    milestone.completed_at = (
        None if milestone.completed_at else datetime.now(timezone.utc)
    )
    db.commit()
    db.refresh(milestone)
    return DreamMilestoneToggleRead(id=milestone.id, completedAt=milestone.completed_at)


@router.patch(
    "/{dream_id}/milestones/{milestone_id}", response_model=DreamMilestoneRead
)
def update_milestone_progress(
    dream_id: int,
    milestone_id: int,
    payload: DreamMilestoneProgressPayload,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dream = _get_user_dream_or_404(db, user.id, dream_id)
    milestone = next(
        (item for item in dream.milestones if item.id == milestone_id), None
    )
    if not milestone:
        raise HTTPException(status_code=404, detail="Marco não encontrado")

    milestone.financial_current_value = payload.financialCurrentValue
    db.flush()
    sync_dream_milestone_financial_progress(db, user.id, dream.id)
    db.commit()
    db.refresh(milestone)
    return DreamMilestoneRead(
        id=milestone.id,
        title=milestone.title,
        targetDate=milestone.target_date,
        completedAt=milestone.completed_at,
        financialTargetValue=milestone.financial_target_value,
        financialCurrentValue=milestone.financial_current_value,
        progressPercent=milestone.progress_percent,
        position=milestone.position,
    )
