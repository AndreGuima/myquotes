from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================
# BASE SOMENTE PARA CAMPOS COMUNS
# ============================
class QuoteBase(BaseModel):
    text: str = Field(..., min_length=1, description="Quote text cannot be empty")


# ============================
# CREATE
# author NÃO é obrigatório
# ============================
class QuoteCreate(QuoteBase):
    author: Optional[str] = None


# ============================
# UPDATE (parcial)
# ============================
class QuoteUpdate(BaseModel):
    author: Optional[str] = None
    text: Optional[str] = Field(None, min_length=1)


# ============================
# READ
# ============================
class QuoteRead(BaseModel):
    id: int
    author: str
    text: str
    user_id: int
    user_name: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
