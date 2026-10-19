from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class WorkerBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    specialty: str | None = Field(default=None, max_length=100)


class WorkerCreate(WorkerBase):
    pass


class WorkerUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    specialty: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class WorkerRead(WorkerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime