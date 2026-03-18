from datetime import datetime
from decimal import Decimal

from models.investment import InvestmentAssetTypeEnum
from pydantic import BaseModel, ConfigDict, Field


class InvestmentCreate(BaseModel):
    asset_type: InvestmentAssetTypeEnum
    sector: str | None = Field(default=None, max_length=120)
    ticker: str = Field(min_length=1, max_length=30)
    name: str | None = Field(default=None, max_length=255)
    quantity: Decimal = Field(gt=0, decimal_places=4)
    average_price: Decimal = Field(ge=0, decimal_places=4)


class InvestmentUpdate(BaseModel):
    asset_type: InvestmentAssetTypeEnum | None = None
    sector: str | None = Field(default=None, max_length=120)
    ticker: str | None = Field(default=None, min_length=1, max_length=30)
    name: str | None = Field(default=None, max_length=255)
    quantity: Decimal | None = Field(default=None, gt=0, decimal_places=4)
    average_price: Decimal | None = Field(default=None, ge=0, decimal_places=4)


class InvestmentRead(BaseModel):
    id: int
    asset_type: InvestmentAssetTypeEnum
    sector: str
    ticker: str
    name: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal | None = None
    price_updated_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class InvestmentPriceHistoryRead(BaseModel):
    id: int
    ticker: str
    price: Decimal
    currency: str
    source: str
    captured_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestmentPriceSyncResult(BaseModel):
    synced_investments: int
    synced_tickers: int
    captured_at: datetime
