from typing import Any, Dict

from models.user_preference import UserPreference
from sqlalchemy.orm import Session

# ============================================================
# 🔧 Core helpers
# ============================================================


def get_user_preferences(
    db: Session,
    user_id: int,
    category: str,
) -> Dict[str, Any]:
    """
    Retorna SOMENTE o dict de preferências.
    Nunca retorna None.
    """
    pref = (
        db.query(UserPreference)
        .filter(
            UserPreference.user_id == user_id,
            UserPreference.category == category,
        )
        .first()
    )

    return pref.preferences if pref and pref.preferences else {}


# ============================================================
# 🔁 Upsert / Merge (coração do sistema)
# ============================================================


def upsert_user_preferences(
    db: Session,
    user_id: int,
    category: str,
    new_preferences: Dict[str, Any],
) -> UserPreference:
    """
    Cria ou atualiza preferências de um usuário por categoria.

    - NÃO sobrescreve tudo
    - Faz merge por chave
    - Seguro para futuras adições
    """

    pref = (
        db.query(UserPreference)
        .filter(
            UserPreference.user_id == user_id,
            UserPreference.category == category,
        )
        .first()
    )

    if pref:
        current = pref.preferences or {}
        pref.preferences = {**current, **new_preferences}
    else:
        pref = UserPreference(
            user_id=user_id,
            category=category,
            preferences=new_preferences,
        )
        db.add(pref)

    db.commit()
    db.refresh(pref)
    return pref


# ============================================================
# 🗑️ Utilitários opcionais
# ============================================================


def delete_user_preferences(
    db: Session,
    user_id: int,
    category: str,
) -> None:
    pref = (
        db.query(UserPreference)
        .filter(
            UserPreference.user_id == user_id,
            UserPreference.category == category,
        )
        .first()
    )

    if pref:
        db.delete(pref)
        db.commit()
