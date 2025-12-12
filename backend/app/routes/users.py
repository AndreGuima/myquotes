from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import hash_password

router = APIRouter(prefix="/admin/users", tags=["Users"])

# ==============================
# 🧱 Schemas
# ==============================
class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    role: str
    is_verified: bool
    is_active: bool
    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    role: str
    password: str | None = None


# ==============================
# 🔁 RESTAURAR USUÁRIO
# ==============================
@router.post("/{user_id}/restore", status_code=200)
def restore_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()

    return {"message": "User restored successfully"}


# ==============================
# 👁 GET LIST
# ==============================
@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# ==============================
# 🔍 GET BY ID
# ==============================
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ==============================
# ✏️ UPDATE USER
# ==============================
@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = payload.username
    user.email = payload.email
    user.role = payload.role

    if payload.password:
        user.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(user)
    return user


# ==============================
# ❌ DELETE USER (LOGICAL DELETE)
# ==============================
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
