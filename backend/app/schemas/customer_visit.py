import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CustomerVisitCreate(BaseModel):
    service_name: str = Field(min_length=1, max_length=150)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    visited_at: datetime | None = None
    notes: str | None = None


class CustomerVisitRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    customer_id: uuid.UUID
    service_name: str
    amount: Decimal
    visited_at: datetime
    notes: str | None

    model_config = ConfigDict(from_attributes=True)
