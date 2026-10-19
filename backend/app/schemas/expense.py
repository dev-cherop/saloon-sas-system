import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PaymentMethod = Literal["cash", "mobile_money", "card", "bank_transfer"]


class ExpenseCreate(BaseModel):
    branch_id: uuid.UUID | None = None
    category: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    expense_date: date
    description: str | None = None
    payment_method: PaymentMethod = "cash"


class ExpenseUpdate(BaseModel):
    branch_id: uuid.UUID | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    amount: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    expense_date: date | None = None
    description: str | None = None
    payment_method: PaymentMethod | None = None


class ExpenseRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    branch_id: uuid.UUID | None
    category: str
    amount: Decimal
    expense_date: date
    description: str | None
    payment_method: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
