"""Module that contains thread service class."""

from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models.thread import Thread, ThreadCreateData
from app.api.v1.repositories.thread import ThreadRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class ThreadService(BaseService):
    """Thread service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: ThreadRepository = Depends(),
    ) -> None:
        """Initializes the thread service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (ThreadRepository):  An instance of the Thread repository.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

    async def get(self, *_: Any) -> Any:
        """Retrieves a list of threads based on parameters.

        Args:
            _ (Any): Parameters for list filtering, searching, sorting and pagination.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of threads.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(self, *_: Any) -> int:
        """Counts threads based on parameters.

        Args:
            _ (Any): Parameters for list filtering and searching.

        Returns:
            int: Count of threads.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(self, id_: ObjectId) -> Thread:
        """Retrieves a thread by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the thread.

        Returns:
            Thread: The retrieved thread.

        """

        return await self.repository.get_by_id(id_=id_)

    async def create(self, data: ThreadCreateData) -> Thread:
        """Creates a new thread.

        Args:
            data (ThreadCreateData): The data for the new thread.

        Returns:
            Thread: Created thread.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update(self, item: Any, data: Any) -> Any:
        """Updates a thread object.

        Args:
            item (Any): Thread object.
            data (Any): Data to update thread.

        Returns:
            Any: The updated thread.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, data: Any) -> Any:
        """Updates a thread by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the thread.
            data (Any): Data to update thread.

        Returns:
            Any: The updated thread.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a thread by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the thread.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete(self, item: Any) -> None:
        """Deletes a thread.

        Args:
            item (Any): Thread object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
