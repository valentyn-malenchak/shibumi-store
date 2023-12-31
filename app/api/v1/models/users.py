"""Module that contains users domain models."""

from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints

from app.api.v1.models.auth import TokenUserModel
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
    created_at: datetime
    updated_at: datetime | None

    def get_token_data(self) -> TokenUserModel:
        """Extracts user data used for JWT generation."""

        token_data = {
            field_name: getattr(self, field_name)
            for field_name, field_type in TokenUserModel.__annotations__.items()
        }

        return TokenUserModel(**token_data)


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
