from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserLogin, UserRead


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


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

    # Criar token JWT
    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user)
    }
