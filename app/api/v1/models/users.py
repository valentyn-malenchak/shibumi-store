"""Module that contains users domain models."""

from datetime import date

from pydantic import BaseModel, EmailStr

from app.api.v1.models.auth import TokenUserModel
from app.utils.pydantic import ObjectId


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
