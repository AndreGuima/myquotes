from datetime import date
from hashlib import sha256

from models.quote import Quote
from sqlalchemy.orm import Session


def get_quote_of_the_day_for_user(db: Session, user_id: int) -> Quote:
    """
    Retorna a Quote of the Day determinística para um usuário.
    """

    quotes = db.query(Quote).filter(Quote.user_id == user_id).order_by(Quote.id).all()

    if not quotes:
        raise ValueError("Nenhuma quote encontrada para este usuário.")

    today = date.today().isoformat()
    key = f"{user_id}-{today}"

    digest = sha256(key.encode()).hexdigest()
    index = int(digest, 16) % len(quotes)

    return quotes[index]
