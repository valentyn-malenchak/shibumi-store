"""Module that contains parameter service class."""


from typing import Any, List, Mapping

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.repositories.parameter import ParameterRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class ParameterService(BaseService):
    """Parameter service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        repository: ParameterRepository = Depends(),
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
    ) -> None:
        """Initializes the parameter service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            repository (ParameterRepository): An instance of the Parameter repository.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

    async def get(self, *_: Any) -> List[Mapping[str, Any]]:
        """Retrieves a list of parameters based on parameters.

        Args:
            _ (Any): Parameters for list filtering, searching, sorting and pagination.

        Returns:
            List[Mapping[str, Any]]: The retrieved list of parameters.

        """
        return await self.repository.get()

    async def count(self, *_: Any) -> int:
        """Counts documents based on parameters.

        Args:
             _ (Any): Parameters for list filtering and searching.

        Returns:
            int: Count of documents.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(self, id_: ObjectId) -> Any:
        """Retrieves a parameter by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the parameter.

        Returns:
            Any: The retrieved parameter or None if not found.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(self, item: Any) -> Any:
        """Creates a new parameter.

        Args:
            item (Any): The data for the new parameter.

        Returns:
            Any: The ID of created parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, item: Any) -> Any:
        """Updates a parameter by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the parameter.
            item (Any): Data to update parameter.

        Returns:
            Any: The updated parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a parameter by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
