from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field("user", pattern="^(admin|editor|user)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=4)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=4)
    role: Optional[str] = Field(None, pattern="^(admin|editor|user)$")

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str

class UserToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
