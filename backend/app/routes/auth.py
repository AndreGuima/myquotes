from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.core.security import verify_password, create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])


# =====================================================
# 🔐 LOGIN (AGORA POR EMAIL)
# =====================================================
@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Buscar usuário por email
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })

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
        role=payload.role or "user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Usuário criado com sucesso",
        "user": UserRead.model_validate(new_user),
    }
