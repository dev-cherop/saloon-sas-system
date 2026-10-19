from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    duration_minutes: int = Field(default=30, gt=0, le=1440)


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    duration_minutes: int | None = Field(default=None, gt=0, le=1440)
    is_active: bool | None = None


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    name: str
    description: str | None
    price: Decimal
    duration_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime