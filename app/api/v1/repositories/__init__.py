"""Module that contains base repository abstract class."""

import abc
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import Depends

from app.services.mongo.service import MongoDBService


class BaseRepository(abc.ABC):
    """Base repository for handling data access operations."""

    def __init__(self, mongo: MongoDBService = Depends()) -> None:
        """Initializes the BaseRepository.

        This method sets up the MongoDB service instance for data access.

        Args:
            mongo (MongoDBService): An instance of the MongoDB service.

        """
        self._mongo = mongo

    @abc.abstractmethod
    async def get_item_by_id(self, id_: ObjectId) -> Any:
        """Retrieves an item from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.

        Returns:
            Any: The retrieved item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create_items(self, items: List[Dict[str, Any]]) -> List[ObjectId]:
        """Creates bulk items in the repository.

        Args:
            items (List[Dict[str, Any]]): Items to be created.

        Returns:
            List[ObjectId]: The created items.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_all_items(self) -> None:
        """Deletes all items from the repository.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError
