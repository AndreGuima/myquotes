from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BankAccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    objective_dream_id: int
    total_value: Decimal = Field(ge=0, decimal_places=2)


class BankAccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    objective_dream_id: int | None = None
    total_value: Decimal | None = Field(default=None, ge=0, decimal_places=2)


class BankAccountRead(BaseModel):
    id: int
    name: str
    objective_dream_id: int
    objective_dream_title: str
    total_value: Decimal
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PatrimonySnapshotRead(BaseModel):
    class AccountSnapshotRead(BaseModel):
        bank_account_id: int | None = None
        account_name: str
        total_value: Decimal

        model_config = ConfigDict(from_attributes=True)

    id: int
    total_value: Decimal
    has_breakdown: bool = False
    snapshot_at: datetime
    accounts: list[AccountSnapshotRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
