"""Module that contains user domain models."""

from datetime import date, datetime

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
    email_verified: bool
    hashed_password: str
    phone_number: str
    birthdate: date
    roles: list[RolesEnum]
    deleted: bool
    created_at: datetime
    updated_at: datetime | None

    @property
    def is_client(self) -> bool:
        """Shows is user a client or belongs to shop side."""
        return self.roles == [RolesEnum.CUSTOMER]


class CurrentUserModel(BaseModel):
    """User model for authenticate/authorize operations."""

    object: User
    scopes: list[str]


class UserResponseModel(ObjectIdModel):
    """User response model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    username: str
    email: EmailStr
    email_verified: bool
    phone_number: str
    birthdate: date
    roles: list[str]
    deleted: bool
    created_at: datetime
    updated_at: datetime | None


class UsersFilterModel(BaseModel):
    """Users list filter model."""

    roles: list[RolesEnum] = Field(Query([]))
    deleted: bool | None = None


class UsersListModel(ListResponseModel):
    """Users list model."""

    data: list[UserResponseModel]


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
    roles: list[RolesEnum]


class UpdateUserRequestModel(BaseModel):
    """User updating request model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    phone_number: PhoneNumber
    birthdate: date
    roles: list[RolesEnum]


class UserPasswordUpdateModel(BaseModel):
    """User password update model."""

    old_password: str
    new_password: PasswordPolicy


class VerificationTokenModel(BaseModel):
    """Verification token model."""

    token: str


class UserPasswordResetModel(VerificationTokenModel):
    """User password reset model."""

    new_password: PasswordPolicy
