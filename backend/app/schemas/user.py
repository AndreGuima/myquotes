from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ==========================================
# 🧩 Base (campos comuns entre schemas)
# ==========================================
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field("user", pattern="^(admin|editor|user)$")


# ==========================================
# 📝 Schema para criação (input)
# ==========================================
class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


# ==========================================
# 🔄 Schema para atualização (parcial)
# ==========================================
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=4)
    role: Optional[str] = Field(None, pattern="^(admin|editor|user)$")


# ==========================================
# 📤 Schema de leitura (output)
# ==========================================
class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True   # <— importante para SQLAlchemy ORM

