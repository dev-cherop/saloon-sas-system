import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    first_name: str = Field(
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    email: EmailStr | None = None

    preferences: str | None = None


class CustomerUpdate(BaseModel):
    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    email: EmailStr | None = None

    preferences: str | None = None


class CustomerRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    first_name: str
    last_name: str
    phone: str | None
    email: str | None
    preferences: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)