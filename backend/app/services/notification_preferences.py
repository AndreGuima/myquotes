from services.user_preferences_service import get_user_preferences
from sqlalchemy.orm import Session


def is_daily_quote_enabled(
    db: Session,
    user_id: int,
    default: bool = True,
) -> bool:
    """
    Retorna se o usuário deseja receber a quote diária.

    Fonte oficial:
    - user_preferences
      category = "notifications"
      key = "daily_quote"
    """

    prefs = get_user_preferences(
        db=db,
        user_id=user_id,
        category="notifications",
    )

    if not prefs:
        return default

    return bool(prefs.preferences.get("daily_quote", default))
