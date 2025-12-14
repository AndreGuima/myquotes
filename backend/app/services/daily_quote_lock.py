from datetime import date

from models.daily_quote_email_log import DailyQuoteEmailLog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def acquire_daily_email_lock(
    db: Session,
    user_id: int,
) -> bool:
    lock = DailyQuoteEmailLog(
        user_id=user_id,
        date=date.today(),
    )

    db.add(lock)

    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
