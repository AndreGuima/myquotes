from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User
from schemas.preferences import PreferencesResponse, PreferencesUpdate
from services.user_preferences_service import (
    get_user_preferences,
    upsert_user_preferences,
)
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"],
)


# ============================================================
# 📥 GET /preferences/{category}
# ============================================================


@router.get(
    "/{category}",
    response_model=PreferencesResponse,
)
def get_preferences(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preferences = get_user_preferences(
        db=db,
        user_id=current_user.id,
        category=category,
    )

    return {
        "category": category,
        "preferences": preferences,
    }


# ============================================================
# 📤 PUT /preferences/{category}
# ============================================================


@router.put(
    "/{category}",
    response_model=PreferencesResponse,
    status_code=status.HTTP_200_OK,
)
def update_preferences(
    category: str,
    payload: PreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.preferences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferences payload cannot be empty",
        )

    pref = upsert_user_preferences(
        db=db,
        user_id=current_user.id,
        category=category,
        new_preferences=payload.preferences,
    )

    return {
        "category": pref.category,
        "preferences": pref.preferences,
    }
