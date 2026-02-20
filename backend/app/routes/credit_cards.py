from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.credit_card import CreditCard
from models.user import User
from schemas.credit_card import CreditCardCreate, CreditCardRead, CreditCardUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/credit-cards", tags=["Credit Cards"])


def _to_response(card: CreditCard) -> CreditCardRead:
    return CreditCardRead(
        id=card.id,
        name=card.name,
        created_at=card.created_at,
        updated_at=card.updated_at,
    )


def _get_user_card_or_404(db: Session, user_id: int, card_id: int) -> CreditCard:
    card = (
        db.query(CreditCard)
        .filter(CreditCard.id == card_id, CreditCard.user_id == user_id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    return card


@router.get("", response_model=list[CreditCardRead])
def list_credit_cards(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cards = (
        db.query(CreditCard)
        .filter(CreditCard.user_id == user.id)
        .order_by(CreditCard.created_at.desc(), CreditCard.id.desc())
        .all()
    )
    return [_to_response(card) for card in cards]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CreditCardRead)
def create_credit_card(
    payload: CreditCardCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    clean_name = payload.name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Nome é obrigatório")
    exists = (
        db.query(CreditCard)
        .filter(CreditCard.user_id == user.id, CreditCard.name == clean_name)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Cartão já existe")

    card = CreditCard(user_id=user.id, name=clean_name)
    db.add(card)
    db.commit()

    created = _get_user_card_or_404(db, user.id, card.id)
    return _to_response(created)


@router.patch("/{card_id}", response_model=CreditCardRead)
def update_credit_card(
    card_id: int,
    payload: CreditCardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    card = _get_user_card_or_404(db, user.id, card_id)

    if payload.name is not None:
        clean_name = payload.name.strip()
        if not clean_name:
            raise HTTPException(status_code=400, detail="Nome é obrigatório")
        exists = (
            db.query(CreditCard)
            .filter(
                CreditCard.user_id == user.id,
                CreditCard.name == clean_name,
                CreditCard.id != card_id,
            )
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="Cartão já existe")
        card.name = clean_name

    db.commit()

    updated = _get_user_card_or_404(db, user.id, card_id)
    return _to_response(updated)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credit_card(
    card_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    card = _get_user_card_or_404(db, user.id, card_id)
    db.delete(card)
    db.commit()
    return None
