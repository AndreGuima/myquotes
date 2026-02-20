from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreditCardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class CreditCardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)


class CreditCardRead(BaseModel):
    id: int
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
