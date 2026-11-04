import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


PayrollStatus = Literal["draft", "approved", "paid"]
PaymentMethod = Literal["cash", "mobile_money", "card", "bank_transfer"]


class PayrollCreate(BaseModel):
    worker_id: uuid.UUID
    period_start: date
    period_end: date
    base_pay: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    commission: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)
    bonus: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)
    deductions: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_period(self):
        if self.period_end < self.period_start:
            raise ValueError("Pay period end cannot precede its start")
        return self


class PayrollUpdate(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    base_pay: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    commission: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    bonus: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    deductions: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    notes: str | None = None


class PayrollStatusUpdate(BaseModel):
    status: Literal["approved", "paid"]
    payment_method: PaymentMethod | None = None


class PayrollRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    worker_id: uuid.UUID
    period_start: date
    period_end: date
    base_pay: Decimal
    commission: Decimal
    bonus: Decimal
    deductions: Decimal
    net_pay: Decimal
    status: PayrollStatus
    payment_method: str | None
    paid_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)