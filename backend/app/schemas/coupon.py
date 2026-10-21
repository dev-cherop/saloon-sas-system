from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CouponCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    description: str | None = None
    discount_type: str
    discount_value: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    minimum_spend: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    usage_limit: int | None = Field(default=None, gt=0)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_coupon(self):
        if self.discount_type not in {"percentage", "fixed"}:
            raise ValueError("Discount type must be percentage or fixed")
        if self.discount_type == "percentage" and self.discount_value > 100:
            raise ValueError("Percentage discount cannot exceed 100")
        if self.starts_at and self.expires_at and self.expires_at <= self.starts_at:
            raise ValueError("Expiry must be later than the start date")
        return self


class CouponUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    discount_type: str | None = None
    discount_value: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    minimum_spend: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    usage_limit: int | None = Field(default=None, gt=0)
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_coupon(self):
        if self.discount_type is not None and self.discount_type not in {
            "percentage", "fixed"
        }:
            raise ValueError("Discount type must be percentage or fixed")
        if (
            self.discount_type == "percentage"
            and self.discount_value is not None
            and self.discount_value > 100
        ):
            raise ValueError("Percentage discount cannot exceed 100")
        if self.starts_at and self.expires_at and self.expires_at <= self.starts_at:
            raise ValueError("Expiry must be later than the start date")
        return self


class CouponRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    code: str
    description: str | None
    discount_type: str
    discount_value: Decimal
    minimum_spend: Decimal
    starts_at: datetime | None
    expires_at: datetime | None
    usage_limit: int | None
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
