from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DreamSmartPayload(BaseModel):
    specific: Optional[str] = None
    measurable: Optional[str] = None
    achievable: Optional[str] = None
    relevant: Optional[str] = None
    timeBound: Optional[str] = None
    targetDate: Optional[date] = None


class DreamMilestonePayload(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=1, max_length=200)
    targetDate: Optional[date] = None
    completedAt: Optional[datetime] = None


class DreamCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    smart: DreamSmartPayload = Field(default_factory=DreamSmartPayload)
    linkedHabitIds: list[int] = Field(default_factory=list)
    milestones: list[DreamMilestonePayload] = Field(default_factory=list)


class DreamUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    smart: Optional[DreamSmartPayload] = None
    linkedHabitIds: Optional[list[int]] = None
    milestones: Optional[list[DreamMilestonePayload]] = None


class DreamMilestoneRead(BaseModel):
    id: int
    title: str
    targetDate: Optional[date] = None
    completedAt: Optional[datetime] = None
    position: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DreamSmartRead(BaseModel):
    specific: Optional[str] = None
    measurable: Optional[str] = None
    achievable: Optional[str] = None
    relevant: Optional[str] = None
    timeBound: Optional[str] = None
    targetDate: Optional[date] = None


class DreamRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    smart: DreamSmartRead
    linkedHabitIds: list[int]
    milestones: list[DreamMilestoneRead]
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class DreamMilestoneToggleRead(BaseModel):
    id: int
    completedAt: Optional[datetime] = None
