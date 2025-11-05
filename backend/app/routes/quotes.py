from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.quote import Quote
from ..schemas.quote import QuoteCreate, QuoteRead
from ..database import get_db

router = APIRouter(
    prefix="/quotes",
    tags=["Quotes"]
)


@router.get("/", response_model=list[QuoteRead])
def list_quotes(db: Session = Depends(get_db)):
    return db.query(Quote).all()

@router.post("/", response_model=QuoteRead, status_code=status.HTTP_201_CREATED)
def create_quote(payload: QuoteCreate, db: Session = Depends(get_db)):
    q = Quote(**payload.dict())
    db.add(q)
    db.commit()
    db.refresh(q)
    return q
