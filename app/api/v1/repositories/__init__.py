"""Module that contains base repository abstract class."""

import abc
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.services.mongo.service import MongoDBService


class BaseRepository(abc.ABC):
    """Base repository for handling data access operations."""

    _collection_name: str | None = None

    def __init__(self, mongo: MongoDBService = Depends()) -> None:
        """Initializes the BaseRepository.

        This method sets up the MongoDB service instance for data access.

        Args:
            mongo (MongoDBService): An instance of the MongoDB service.

        """
        self._mongo = mongo

    @abc.abstractmethod
    async def get_item_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Retrieves an item from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create_item(
        self, item: Any, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Create a new item in repository.

        Args:
            item (Any): The data for the new item.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create_items(
        self,
        items: List[Dict[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Any]:
        """Creates bulk items in the repository.

        Args:
            items (List[Dict[str, Any]]): Items to be created.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The IDs of created items.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_all_items(
        self, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all items from the repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError
