import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

PaymentMethod = Literal["cash", "mobile_money", "card", "bank_transfer"]

class PaymentCreate(BaseModel):
    visit_id: uuid.UUID | None = None
    sale_id: uuid.UUID | None = None
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_method: PaymentMethod
    reference: str | None = Field(default=None, max_length=150)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_payment_target(self):
        if (self.visit_id is None) == (self.sale_id is None):
            raise ValueError("Provide exactly one of visit_id or sale_id")
        return self


class PaymentRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    visit_id: uuid.UUID | None
    sale_id: uuid.UUID | None
    amount: Decimal
    payment_method: str
    reference: str | None
    notes: str | None
    paid_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)




