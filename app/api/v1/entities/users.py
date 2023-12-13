"""Module that handles user domain operations."""

from typing import Optional

from app.api.v1.entities import StoredEntity
from app.api.v1.schemas.users import User
from app.services.mongo.constants import MongoCollectionsEnum


class UserEntity(StoredEntity):
    """User entity."""

    def __init__(self) -> None:
        """Initialization method."""

        super().__init__()

        self.collection = self._mongo.get_collection_by_name(
            MongoCollectionsEnum.USERS.value
        )

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username (str): Username.

        Returns:
            User object or None.

        """

        user = await self.collection.find_one({"username": username})

        return User(**user) if user else None
