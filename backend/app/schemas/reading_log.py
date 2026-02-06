from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReadingLogCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=500)
    log_date: Optional[date] = None


class ReadingLogRead(BaseModel):
    id: int
    book_id: int
    log_date: date
    comment: str

    model_config = ConfigDict(from_attributes=True)
