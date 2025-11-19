from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from pydantic import BaseModel, EmailStr, Field

from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])

# ==============================
# 🧱 Schemas
# ==============================

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    role: str

    model_config = {"from_attributes": True}

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
# ❌ DELETE USER
# ==============================
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
