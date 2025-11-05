from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class QuoteBase(BaseModel):
    author: str = Field(..., min_length=1, description="Author name cannot be empty")
    text: str = Field(..., min_length=1, description="Quote text cannot be empty")

class QuoteCreate(QuoteBase):
    pass

class QuoteRead(QuoteBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
