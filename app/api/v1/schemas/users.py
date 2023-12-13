"""Module that contains users domain schemas."""

from pydantic import BaseModel

from app.api.v1.schemas import ObjectId
from app.api.v1.schemas.auth import TokenUserData


class User(ObjectId):
    """User schema."""

    first_name: str
    last_name: str
    username: str
    email: str
    hashed_password: str

    def get_token_data(self) -> TokenUserData:
        """Extracts user data used for JWT generation."""

        token_data = {
            field_name: getattr(self, field_name)
            for field_name, field_type in TokenUserData.__annotations__.items()
        }

        return TokenUserData(**token_data)


class UserResponseSchema(BaseModel):
    """User response schema"""

    id: str
    first_name: str
    last_name: str
    username: str
    email: str
