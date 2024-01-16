"""Module that contains user domain models."""

from datetime import date, datetime
from typing import List

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field

from app.api.v1.constants import RolesEnum
from app.api.v1.models import ListResponseModel, ObjectIdModel
from app.utils.pydantic import (
    PasswordPolicy,
    PhoneNumber,
    UsernamePolicy,
)


class User(ObjectIdModel):
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
    deleted: bool
    created_at: datetime
    updated_at: datetime | None

    @property
    def is_client(self) -> bool:
        """Shows is user a client or belongs to shop side."""
        return self.roles == [RolesEnum.CUSTOMER.name]


class CurrentUserModel(BaseModel):
    """User model for authenticate/authorize operations."""

    object: User
    scopes: List[str]


class UserResponseModel(ObjectIdModel):
    """User response model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    username: str
    email: EmailStr
    phone_number: str
    birthdate: date
    roles: List[str]
    deleted: bool
    created_at: datetime
    updated_at: datetime | None


class UsersFilterModel(BaseModel):
    """Users list filter model."""

    roles: List[RolesEnum] = Field(Query([]))
    deleted: bool | None = None


class UsersListModel(ListResponseModel):
    """Users list model."""

    data: List[UserResponseModel]


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
    roles: List[RolesEnum]


class UpdateUserRequestModel(BaseModel):
    """User updating request model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    email: EmailStr
    phone_number: PhoneNumber
    birthdate: date
    roles: List[RolesEnum]


class UserPasswordUpdateModel(BaseModel):
    """User password update model."""

    old_password: str
    new_password: PasswordPolicy


class UserPasswordResetModel(BaseModel):
    """User password reset model."""

    token: str
    new_password: PasswordPolicy
