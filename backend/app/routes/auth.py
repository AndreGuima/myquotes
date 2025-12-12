from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


# =====================================================
# 🔐 LOGIN
# =====================================================
@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Buscar usuário por email
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    # 🚫 Impedir login se o usuário estiver desativado (deleção lógica)
    if not user.is_active:
        raise HTTPException(
            status_code=403, detail="Usuário desativado. Contate o administrador."
        )

    # Verifica senha
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    # 🚫 Impedir login se email não estiver verificado (exceto admin)
    if not user.is_verified and user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Você precisa verificar seu email antes de fazer login.",
        )

    # Gera token
    token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user),
    }


# =====================================================
# 🔐 REGISTER
# =====================================================
@router.post("/register", status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # Verificar se email já existe
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(400, "Email já está registrado")

    # Criar novo usuário
    new_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="user",
        is_verified=False,  # 🔥 importante
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Usuário criado com sucesso. Verifique seu email.",
        "user": UserRead.model_validate(new_user),
    }


# =====================================================
# 🔐 VERIFICAÇÃO DE EMAIL
# =====================================================


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    # 1) Decodifica token
    data = decode_access_token(token)

    if not data:
        raise HTTPException(400, "Token inválido ou expirado")

    # 2) Confere se o token é do tipo 'verify'
    if data.get("type") != "verify":
        raise HTTPException(400, "Token inválido para verificação de email")

    user_id = int(data.get("sub"))

    # 3) Busca usuário
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado")

    # 4) Se já verificado
    if user.is_verified:
        return {"message": ("Este email já foi verificado previamente.")}

    # 5) Marca como verificado
    user.is_verified = True
    db.commit()

    return {"message": "Email verificado com sucesso! Agora você já pode fazer login."}
