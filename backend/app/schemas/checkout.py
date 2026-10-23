import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CheckoutItemCreate(BaseModel):
    service_id: uuid.UUID
    quantity: int = Field(default=1, ge=1, le=100)


class CheckoutCreate(BaseModel):
    customer_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    coupon_code: str | None = Field(default=None, max_length=50)
    items: list[CheckoutItemCreate] = Field(min_length=1, max_length=100)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_unique_services(self):
        service_ids = [item.service_id for item in self.items]
        if len(service_ids) != len(set(service_ids)):
            raise ValueError(
                "Each service must appear once; use quantity for multiples."
            )
        if self.coupon_code is not None:
            self.coupon_code = self.coupon_code.strip().upper() or None
        return self


class SaleItemRead(BaseModel):
    id: uuid.UUID
    service_id: uuid.UUID | None
    service_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class SaleRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    customer_id: uuid.UUID | None
    branch_id: uuid.UUID | None
    coupon_id: uuid.UUID | None
    coupon_code: str | None
    subtotal: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    status: str
    notes: str | None
    items: list[SaleItemRead]

    model_config = ConfigDict(from_attributes=True)
