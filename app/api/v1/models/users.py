"""Module that contains users domain models."""

from datetime import date, datetime
from typing import List

from pydantic import BaseModel, EmailStr

from app.utils.pydantic import ObjectId, PasswordPolicy, PhoneNumber, UsernamePolicy


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


class CurrentUserModel(BaseModel):
    """User model for authenticate/authorize operations."""

    object: User
    scopes: List[str]


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
    username: UsernamePolicy
    email: EmailStr
    password: PasswordPolicy
    phone_number: PhoneNumber
    birthdate: date


class UpdateUserRequestModel(BaseModel):
    """User updating request model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    email: EmailStr
    password: PasswordPolicy
    phone_number: PhoneNumber
    birthdate: date
