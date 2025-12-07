from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import admin_required
from app.core.security import pwd_context
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])


@router.get("/", response_model=list[UserRead], dependencies=[Depends(admin_required)])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.put(
    "/{user_id}", response_model=UserRead, dependencies=[Depends(admin_required)]
)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado")

    if data.username is not None:
        user.username = data.username

    if data.email is not None:
        if db.query(User).filter(User.email == data.email, User.id != user_id).first():
            raise HTTPException(400, "E-mail já está sendo usado por outro usuário")
        user.email = data.email

    if data.password is not None:
        user.password_hash = pwd_context.hash(data.password)

    if data.role is not None:
        user.role = data.role

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", dependencies=[Depends(admin_required)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado")

    db.delete(user)
    db.commit()
    return {"detail": "Usuário apagado com sucesso"}
