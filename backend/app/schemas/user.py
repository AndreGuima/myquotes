from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ============================================================
# ENUM DE ROLES
# ============================================================
class RoleEnum(str, Enum):
    admin = "admin"
    editor = "editor"
    user = "user"


# ============================================================
# BASE
# ============================================================
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None


# ============================================================
# CREATE — REGISTRO (não herda UserBase!)
# ============================================================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str
    confirm_password: str
    role: RoleEnum = RoleEnum.user

    @field_validator("password")
    def validate_password_length(cls, v):
        if len(v) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        return v

    @field_validator("confirm_password", mode="after")
    def validate_confirm_password(cls, v, info):
        pwd = info.data.get("password")
        if pwd and v != pwd:
            raise ValueError("As senhas não coincidem.")
        return v


# ============================================================
# UPDATE
# ============================================================
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[RoleEnum] = None


# ============================================================
# READ (retorno)
# ============================================================
class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    created_at: Optional[datetime]
    is_active: bool = True
    is_verified: bool = False

    # equivale ao antigo orm_mode=True
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# LOGIN
# ============================================================
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# TOKEN
# ============================================================
class UserToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
