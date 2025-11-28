from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

# ============================================================
# BASE
# ============================================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field("user", pattern="^(admin|editor|user)$")


# ============================================================
# CREATE — REGISTRO (não herda UserBase!)
# ============================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str
    confirm_password: str

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
# UPDATE (opcional)
# ============================================================

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = Field(None, pattern="^(admin|editor|user)$")


# ============================================================
# READ (retorno)
# ============================================================

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: Optional[datetime]

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
