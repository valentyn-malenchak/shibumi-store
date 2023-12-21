"""Module that contains user service abstract class."""

from typing import Any, Dict, List

from bson import ObjectId
from fastapi import Depends
from injector import inject

from app.api.v1.models.users import User
from app.api.v1.repositories.users import UserRepository
from app.api.v1.services import BaseService


@inject
class UserService(BaseService):
    """Base service for encapsulating business logic."""

    def __init__(self, repository: UserRepository = Depends()) -> None:
        """Initializes the UserRepository.

        This method sets up the MongoDB service instance for data access.

        Args:
            repository (UserRepository): An instance of the User repository.

        """

        self.repository = repository

    async def get_item_by_id(self, id_: ObjectId) -> User | None:
        """Retrieves an item by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.

        Returns:
            User | None: User object or None.

        """
        return await self.repository.get_item_by_id(id_=id_)

    async def get_item_by_username(self, username: str) -> User | None:
        """Retrieves an item by its username.

        Args:
            username (str): Username.

        Returns:
            User | None: User object or None.

        """
        return await self.repository.get_item_by_username(username=username)

    async def create_items(self, items: List[Dict[str, Any]]) -> List[ObjectId]:
        """Creates new users.

        Args:
            items (List[Dict[str, Any]]): The data for the new items.

        Returns:
            List[ObjectId]: The created items.

        """
        return await self.repository.create_items(items=items)

    async def delete_all_items(self) -> None:
        """Deletes all users."""
        await self.repository.delete_all_items()
