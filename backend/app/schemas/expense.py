from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

PaymentMethod = Literal["debit", "credit"]


class ExpenseCreate(BaseModel):
    value: Decimal = Field(ge=0, decimal_places=2)
    description: str = Field(min_length=1, max_length=255)
    expense_category_id: int
    payment_method: PaymentMethod
    bank_account_id: int | None = None
    credit_card_id: int | None = None
    launch_date: date

    @model_validator(mode="after")
    def validate_payment_reference(self):
        if self.payment_method == "debit":
            if self.bank_account_id is None:
                raise ValueError("bank_account_id is required for debit")
            if self.credit_card_id is not None:
                raise ValueError("credit_card_id must be null for debit")

        if self.payment_method == "credit":
            if self.credit_card_id is None:
                raise ValueError("credit_card_id is required for credit")
            if self.bank_account_id is not None:
                raise ValueError("bank_account_id must be null for credit")

        return self


class ExpenseUpdate(BaseModel):
    value: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    description: str | None = Field(default=None, min_length=1, max_length=255)
    expense_category_id: int | None = None
    payment_method: PaymentMethod | None = None
    bank_account_id: int | None = None
    credit_card_id: int | None = None
    launch_date: date | None = None


class ExpenseRead(BaseModel):
    id: int
    value: Decimal
    description: str
    expense_category_id: int
    expense_category_name: str
    payment_method: PaymentMethod
    bank_account_id: int | None = None
    bank_account_name: str | None = None
    credit_card_id: int | None = None
    credit_card_name: str | None = None
    invoice_payment_expense_id: int | None = None
    launch_date: date
    invoice_paid_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PayCreditInvoiceRequest(BaseModel):
    credit_card_id: int
    bank_account_id: int
    expense_ids: list[int] = Field(min_length=1)
    launch_date: date
    description: str | None = Field(default=None, min_length=1, max_length=255)
    expense_category_id: int | None = None


class PayCreditInvoiceResponse(BaseModel):
    payment_expense: ExpenseRead
    paid_expense_ids: list[int]
    total_paid: Decimal


class ExpenseSummaryCategoryRead(BaseModel):
    category_id: int
    category_name: str
    total: Decimal
    count: int


class ExpenseSummaryRead(BaseModel):
    total: Decimal
    average: Decimal
    count: int
    credit_total: Decimal
    debit_total: Decimal
    by_category: list[ExpenseSummaryCategoryRead]
