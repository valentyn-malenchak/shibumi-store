"""Module that contains user repository class."""

from typing import Any, Dict, List

from bson import ObjectId
from fastapi import Depends
from injector import inject

from app.api.v1.models.users import User
from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum
from app.services.mongo.service import MongoDBService


@inject
class UserRepository(BaseRepository):
    """User repository for handling data access operations."""

    def __init__(self, mongo: MongoDBService = Depends()) -> None:
        """Initializes the UserRepository.

        This method sets up the MongoDB service instance for data access.

        Args:
            mongo (MongoDBService): An instance of the MongoDB service.

        """

        super().__init__(mongo=mongo)

        self.users_collection = MongoCollectionsEnum.USERS.value

    async def get_item_by_id(self, id_: ObjectId) -> User | None:
        """Retrieves a user from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.

        Returns:
            User | None: User object or None.

        """

        user = await self._mongo.find_one(
            collection=self.users_collection, filter_={"_id": id_}
        )

        return User(**user) if user else None

    async def get_item_by_username(self, username: str) -> User | None:
        """Retrieves a user from the repository by its username.

        Args:
            username (str): Username.

        Returns:
            User | None: User object or None.

        """

        user = await self._mongo.find_one(
            collection=self.users_collection, filter_={"username": username}
        )

        return User(**user) if user else None

    async def create_items(self, items: List[Dict[str, Any]]) -> List[ObjectId]:
        """Creates bulk users in the repository.

        Args:
            items (List[Dict[str, Any]]): Users to be created.

        Returns:
            List[ObjectId]: The IDs of created users.

        """

        return await self._mongo.insert_many(
            collection=self.users_collection, documents=items
        )

    async def delete_all_items(self) -> None:
        """Deletes all users from the repository."""
        await self._mongo.delete_many(collection=self.users_collection)
