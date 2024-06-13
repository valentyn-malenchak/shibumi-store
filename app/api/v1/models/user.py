"""Module that contains user domain models."""

from datetime import date, datetime

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field

from app.api.v1.constants import RolesEnum
from app.api.v1.models import BSONObjectId, List
from app.utils.pydantic import (
    PasswordPolicy,
    PhoneNumber,
    UsernamePolicy,
)


class User(BSONObjectId):
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


class CurrentUser(BaseModel):
    """User model for authenticate/authorize operations."""

    object: User
    scopes: list[str]


class ShortUser(BSONObjectId):
    """Short user model."""

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


class UserFilter(BaseModel):
    """User filter model."""

    roles: list[RolesEnum] = Field(Query([]))
    deleted: bool | None = None


class UserList(List):
    """User list model."""

    data: list[ShortUser]


class UserCreateData(BaseModel):
    """User create data model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    username: UsernamePolicy
    email: EmailStr
    password: PasswordPolicy
    phone_number: PhoneNumber
    birthdate: date
    roles: list[RolesEnum]


class UserUpdateData(BaseModel):
    """User update data model."""

    first_name: str
    last_name: str
    patronymic_name: str | None
    email: EmailStr
    phone_number: PhoneNumber
    birthdate: date
    roles: list[RolesEnum]


class UserPasswordUpdateData(BaseModel):
    """User password update data model."""

    old_password: str
    new_password: PasswordPolicy


class VerificationToken(BaseModel):
    """Verification token model."""

    token: str


class UserPasswordResetData(VerificationToken):
    """User password reset data model."""

    new_password: PasswordPolicy
