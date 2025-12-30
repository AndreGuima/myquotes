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
) -> UserPreference | None:
    return (
        db.query(UserPreference)
        .filter(
            UserPreference.user_id == user_id,
            UserPreference.category == category,
        )
        .first()
    )


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

    pref = get_user_preferences(db, user_id, category)

    if pref:
        # Merge defensivo
        current = pref.preferences or {}
        merged = {**current, **new_preferences}
        pref.preferences = merged
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
    pref = get_user_preferences(db, user_id, category)

    if pref:
        db.delete(pref)
        db.commit()
