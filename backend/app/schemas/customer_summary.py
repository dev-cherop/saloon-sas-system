from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CustomerServiceSummary(BaseModel):
    service_name: str
    visit_count: int
    total_spent: Decimal


class CustomerSpendingSummary(BaseModel):
    customer_id: UUID
    total_visits: int
    total_spent: Decimal
    average_spend: Decimal
    last_visit: datetime | None
    most_frequent_services: list[CustomerServiceSummary]

    model_config = ConfigDict(from_attributes=True)
