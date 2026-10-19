
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LoyaltyTransactionRead(BaseModel):
    id: UUID
    business_id: UUID
    customer_id: UUID
    points_change: int
    transaction_type: str
    monetary_value: Decimal
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoyaltyBalanceRead(BaseModel):
    customer_id: UUID
    balance: int
    history: list[LoyaltyTransactionRead]


class LoyaltyRedeem(BaseModel):
    points: int = Field(gt=0)
    description: str | None = Field(default=None, max_length=500)




class LoyaltySettingsRead(BaseModel):
    business_id: UUID
    enabled: bool
    spend_per_point: Decimal
    redemption_value: Decimal
    minimum_redemption_points: int

    model_config = ConfigDict(from_attributes=True)


class LoyaltySettingsUpdate(BaseModel):
    enabled: bool
    spend_per_point: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    redemption_value: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    minimum_redemption_points: int = Field(ge=1)
