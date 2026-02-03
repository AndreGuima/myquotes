from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReadingStatus(str, Enum):
    to_read = "to_read"
    reading = "reading"
    read = "read"


class ReadingListBookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, max_length=150)
    status: ReadingStatus = ReadingStatus.to_read
    rating: Optional[int] = Field(default=None, ge=1, le=5)

    @model_validator(mode="after")
    def validate_rating(self):
        if self.rating is not None and self.status == ReadingStatus.to_read:
            raise ValueError("rating só é permitido para livros em leitura ou lidos")
        return self


class ReadingListBookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, max_length=150)
    status: Optional[ReadingStatus] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)

    @model_validator(mode="after")
    def validate_rating(self):
        if self.rating is not None and self.status == ReadingStatus.to_read:
            raise ValueError("rating só é permitido para livros em leitura ou lidos")
        return self


class ReadingListBookRead(BaseModel):
    id: int
    user_id: int
    title: str
    author: Optional[str]
    status: ReadingStatus
    rating: Optional[int]

    model_config = ConfigDict(from_attributes=True)
