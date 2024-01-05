"""Module that contains users domain models."""

from datetime import date, datetime
from typing import Annotated, List

from pydantic import BaseModel, EmailStr, StringConstraints

from app.utils.pydantic import ObjectId, PhoneNumber


class User(ObjectId):
    """User model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    username: str
    email: EmailStr
    hashed_password: str
    phone_number: str
    birthdate: date
    roles: List[str]
    created_at: datetime
    updated_at: datetime | None


class UserResponseModel(BaseModel):
    """User response model."""

    id: str
    first_name: str
    last_name: str
    patronymic_name: str | None
    username: str
    email: EmailStr
    phone_number: str
    birthdate: date
    roles: List[str]
    created_at: datetime
    updated_at: datetime | None


class CreateUserRequestModel(BaseModel):
    """User creation request model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    username: str
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=20)]
    phone_number: PhoneNumber
    birthdate: date


class UpdateUserRequestModel(BaseModel):
    """User updating request model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=20)]
    phone_number: PhoneNumber
    birthdate: date
