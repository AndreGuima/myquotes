from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IncomeType = Literal["dividend", "jcp", "rendimento"]


class InvestmentIncomeCreate(BaseModel):
    income_type: IncomeType = "dividend"
    ticker: str = Field(min_length=1, max_length=30)
    bank_account_id: int
    received_at: date
    amount: Decimal = Field(gt=0, decimal_places=2)
    notes: str = Field(default="", max_length=500)


class InvestmentIncomeUpdate(BaseModel):
    income_type: IncomeType | None = None
    ticker: str | None = Field(default=None, min_length=1, max_length=30)
    bank_account_id: int | None = None
    received_at: date | None = None
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    notes: str | None = Field(default=None, max_length=500)


class InvestmentIncomeRead(BaseModel):
    id: int
    income_type: IncomeType
    ticker: str
    bank_account_id: int | None = None
    bank_account_name: str | None = None
    received_at: date
    amount: Decimal
    notes: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
