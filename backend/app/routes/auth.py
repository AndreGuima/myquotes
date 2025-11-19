from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.core.security import (
    verify_password,
    create_access_token,
    hash_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

# =====================================================
# 🔐 LOGIN
# =====================================================
@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.username == payload.username)
        .first()
    )

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user)
    }


# =====================================================
# 🔐 REGISTER
# =====================================================
@router.post("/register", status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):

    # Verificar duplicidade username OR email
    existing = (
        db.query(User)
        .filter(
            (User.username == payload.username) |
            (User.email == payload.email)
        )
        .first()
    )

    if existing:
        raise HTTPException(400, "Usuário já existe")

    new_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role if payload.role else "user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Usuário criado com sucesso",
        "user": UserRead.model_validate(new_user)
    }
