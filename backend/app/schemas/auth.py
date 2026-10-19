import uuid

from pydantic import BaseModel, EmailStr,ConfigDict


class UserRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str


class BusinessContextRead(BaseModel):
    id: uuid.UUID
    name: str
    role: str
    permissions: list[str]


class AuthContextRead(BaseModel):
    user: UserRead
    businesses: list[BusinessContextRead]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead