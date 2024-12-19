"""Module that contains base service abstract class.

Service rules:

- Defines API interactions for each entity.
- In most cases should use own repository, but repositories of other entities are
also allowed. It ensures flexible transaction support.
- Services are the only layer that can use repositories.
- Can't use other entity services or MongoService.
- Are not aware of HTTP requests.

"""

import abc
from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class BaseService(abc.ABC):
    """Base service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
    ) -> None:
        """Initializes the BaseService.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.

        """

        self.background_tasks = background_tasks

        self.redis_service = redis_service

        self.transaction_manager = transaction_manager

    @abc.abstractmethod
    async def get(self, **kwargs: Any) -> list[Any]:
        """Retrieves a list of items based on parameters.

        Args:
            kwargs (Any): Keyword parameters.

        Returns:
            list[Any]: The retrieved list of items.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def count(self, **kwargs: Any) -> int:
        """Counts items based on parameters.

        Args:
            kwargs (Any): Keyword parameters.

        Returns:
            int: Count of items.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, id_: ObjectId) -> Any:
        """Retrieves an item by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.

        Returns:
            Any: The retrieved item or None if not found.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self, data: Any) -> Any:
        """Creates a new item.

        Args:
            data (Any): The data for the new item.

        Returns:
            Any: Created item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, item: Any, data: Any) -> Any:
        """Updates an item.

        Args:
            item (Any): Current item object.
            data (Any): Data to update item.

        Returns:
            Any: The updated item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update_by_id(self, id_: ObjectId, data: Any) -> Any:
        """Updates an item by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.
            data (Any): Data to update item.

        Returns:
            Any: The updated item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes an item by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, item: Any) -> None:
        """Deletes an item.

        Args:
            item (Any): Current item object.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError
