from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class QuoteBase(BaseModel):
    author: str = Field(..., min_length=1, description="Author name cannot be empty")
    text: str = Field(..., min_length=1, description="Quote text cannot be empty")

class QuoteCreate(QuoteBase):
    pass

class QuoteUpdate(BaseModel):
    author: Optional[str] = Field(None, min_length=1)
    text: Optional[str] = Field(None, min_length=1)

class QuoteRead(BaseModel):
    id: int
    author: str
    text: str
    user_id: int
    user_name: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
