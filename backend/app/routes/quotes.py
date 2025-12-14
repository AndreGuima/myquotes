from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from database import get_db
from models.quote import Quote
from models.user import User
from schemas.quote import QuoteCreate, QuoteRead, QuoteUpdate

router = APIRouter(prefix="/quotes", tags=["Quotes"])


# ==============================
# 🔍 LISTAR QUOTES
# ==============================
@router.get("", response_model=list[QuoteRead])
def list_quotes(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # ===========================
    # ADMIN: retorna todas as quotes
    # ===========================
    if current_user.role == "admin":
        result = (
            db.query(Quote, User.username.label("user_name"))
            .join(User, User.id == Quote.user_id)
            .order_by(Quote.id)
            .all()
        )

    # ===========================
    # USUÁRIO NORMAL: retorna apenas suas quotes
    # ===========================
    else:
        result = (
            db.query(Quote, User.username.label("user_name"))
            .join(User, User.id == Quote.user_id)
            .filter(Quote.user_id == current_user.id)
            .order_by(Quote.id)
            .all()
        )

    # Converte o resultado
    quotes = [
        QuoteRead(
            id=quote.id,
            author=quote.author,
            text=quote.text,
            user_id=quote.user_id,
            user_name=user_name,
            created_at=quote.created_at,
        )
        for quote, user_name in result
    ]

    return quotes


# ==============================
# ➕ CRIAR QUOTE (AUTENTICADO)
# ==============================
@router.post("", response_model=QuoteRead, status_code=status.HTTP_201_CREATED)
def create_quote(
    payload: QuoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = Quote(
        **payload.model_dump(),
        user_id=current_user.id,
    )

    db.add(q)
    db.commit()
    db.refresh(q)
    return q


# ==============================
# ✏️ ATUALIZAR QUOTE (PERMISSÃO)
# ==============================
@router.put("/{quote_id}", response_model=QuoteRead)
def update_quote(
    quote_id: int,
    payload: QuoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Quote).filter(Quote.id == quote_id).first()
    if not q:
        raise HTTPException(404, "Quote not found")

    # Permissão: proprietário ou admin
    if q.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Você não pode editar esta quote.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(q, key, value)

    db.commit()
    db.refresh(q)
    return q


# ==============================
# ❌ DELETAR QUOTE (PERMISSÃO)
# ==============================
@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Quote).filter(Quote.id == quote_id).first()
    if not q:
        raise HTTPException(404, "Quote not found")

    # Permissão
    if q.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Você não pode deletar esta quote.")

    db.delete(q)
    db.commit()


# ==============================
# ⭐ QUOTE OF THE DAY (DETERMINÍSTICO)
# ==============================
@router.get("/of-the-day", response_model=QuoteRead)
def quote_of_the_day(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    quotes = (
        db.query(Quote)
        .filter(Quote.user_id == current_user.id)
        .order_by(Quote.id)
        .all()
    )

    if not quotes:
        raise HTTPException(404, "Nenhuma quote encontrada para este usuário.")

    from datetime import date
    from hashlib import sha256

    today = date.today().isoformat()
    key = f"{current_user.id}-{today}"

    digest = sha256(key.encode()).hexdigest()
    index = int(digest, 16) % len(quotes)

    return quotes[index]


# ==============================
# 🔍 OBTER UMA QUOTE
# ==============================
@router.get("/{quote_id:int}", response_model=QuoteRead)
def get_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Quote).filter(Quote.id == quote_id).first()

    if not q:
        raise HTTPException(404, "Quote not found")

    if q.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Você não pode acessar esta quote.")

    return q
