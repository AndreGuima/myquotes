from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.quote import Quote
from ..schemas.quote import QuoteCreate, QuoteRead, QuoteUpdate
from ..database import get_db

router = APIRouter(
    prefix="/quotes",
    tags=["Quotes"]
)

@router.get("/", response_model=list[QuoteRead])
def list_quotes(db: Session = Depends(get_db)):
    from app.models.user import User

    # Join para trazer o nome do usuário
    result = (
        db.query(Quote, User.username.label("user_name"))
        .join(User, User.id == Quote.user_id)
        .order_by(Quote.id)
        .all()
    )

    # Converte resultados
    quotes = []
    for quote, user_name in result:
        quotes.append(
            QuoteRead(
                id=quote.id,
                author=quote.author,
                text=quote.text,
                user_id=quote.user_id,
                user_name=user_name,
                created_at=quote.created_at,
            )
        )

    return quotes


@router.get("/{quote_id}", response_model=QuoteRead)
def get_quote(quote_id: int, db: Session = Depends(get_db)):
    q = db.query(Quote).filter(Quote.id == quote_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")
    return q

@router.post("/", response_model=QuoteRead, status_code=status.HTTP_201_CREATED)
def create_quote(payload: QuoteCreate, db: Session = Depends(get_db)):
    DEFAULT_TEST_USER_ID = 1  # temporário até implementarmos auth

    q = Quote(
        **payload.model_dump(),
        user_id=DEFAULT_TEST_USER_ID
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

@router.put("/{quote_id}", response_model=QuoteRead)
def update_quote(quote_id: int, payload: QuoteUpdate, db: Session = Depends(get_db)):
    q = db.query(Quote).filter(Quote.id == quote_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(q, key, value)

    db.commit()
    db.refresh(q)
    return q

@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    q = db.query(Quote).filter(Quote.id == quote_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")

    db.delete(q)
    db.commit()
