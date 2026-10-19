import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PaymentMethod = Literal["cash", "mobile_money", "card", "bank_transfer"]


class PaymentCreate(BaseModel):
    visit_id: uuid.UUID
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_method: PaymentMethod
    reference: str | None = Field(default=None, max_length=150)
    notes: str | None = None


class PaymentRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    visit_id: uuid.UUID
    amount: Decimal
    payment_method: str
    reference: str | None
    notes: str | None
    paid_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)






