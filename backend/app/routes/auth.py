from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not user.is_active:
        raise HTTPException(
            status_code=403, detail="Usuário desativado. Contate o administrador."
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    if not user.is_verified and user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Você precisa verificar seu email antes de fazer login.",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user),
    }


@router.post("/register", status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(400, "Email já está registrado")

    new_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="user",
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Usuário criado com sucesso. Verifique seu email.",
        "user": UserRead.model_validate(new_user),
    }


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    data = decode_access_token(token)

    if not data:
        raise HTTPException(400, "Token inválido ou expirado")

    if data.get("type") != "verify":
        raise HTTPException(400, "Token inválido para verificação de email")

    user = db.query(User).filter(User.id == int(data.get("sub"))).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado")

    if user.is_verified:
        return {"message": "Este email já foi verificado previamente."}

    user.is_verified = True
    db.commit()

    return {"message": "Email verificado com sucesso! Agora você já pode fazer login."}
