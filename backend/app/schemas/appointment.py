from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


AppointmentStatus = Literal[
    "scheduled",
    "confirmed",
    "completed",
    "cancelled",
    "no_show",
]


class AppointmentCreate(BaseModel):
    customer_id: UUID
    service_id: UUID
    worker_id: UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = "scheduled"
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class AppointmentUpdate(BaseModel):
    customer_id: UUID | None = None
    service_id: UUID | None = None
    worker_id: UUID | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: AppointmentStatus | None = None
    notes: str | None = Field(default=None, max_length=2000)


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    customer_id: UUID
    service_id: UUID
    worker_id: UUID
    start_time: datetime
    end_time: datetime
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
