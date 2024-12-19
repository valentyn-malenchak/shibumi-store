"""Module that contains parameter service class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId, json_util
from fastapi import BackgroundTasks, Depends

from app.api.v1.repositories.parameter import ParameterRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.constants import RedisNamesEnum, RedisNamesTTLEnum
from app.services.redis.service import RedisService


class ParameterService(BaseService):
    """Parameter service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: ParameterRepository = Depends(),
    ) -> None:
        """Initializes the parameter service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (ParameterRepository): An instance of the Parameter repository.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

    async def get(self, **kwargs: Any) -> list[Mapping[str, Any]]:
        """Retrieves a list of parameters based on parameters.

        Args:
            kwargs (Any): Keyword parameters.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of parameters.

        """

        cached_parameters = await self.redis_service.get(
            name=RedisNamesEnum.PRODUCT_PARAMETERS_LIST
        )

        if cached_parameters is not None:
            return json_util.loads(cached_parameters)  # type: ignore

        parameters = await self.repository.get()

        await self.redis_service.set(
            name=RedisNamesEnum.PRODUCT_PARAMETERS_LIST,
            value=json_util.dumps(parameters),
            ttl=RedisNamesTTLEnum.PRODUCT_PARAMETERS_LIST.value,
        )

        return parameters

    async def count(self, **kwargs: Any) -> int:
        """Counts parameters based on parameters.

        Args:
            kwargs (Any): Keyword parameters.

        Returns:
            int: Count of parameters.

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

    async def create(self, data: Any) -> Any:
        """Creates a new parameter.

        Args:
            data (Any): The data for the new parameter.

        Returns:
            Any: Created parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update(self, item: Any, data: Any) -> Any:
        """Updates a parameter object.

        Args:
            item (Any): Parameter object.
            data (Any): Data to update parameter.

        Returns:
            Any: The updated parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, data: Any) -> Any:
        """Updates a parameter by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the parameter.
            data (Any): Data to update parameter.

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

    async def delete(self, item: Any) -> None:
        """Deletes a parameter.

        Args:
            item (Any): Parameter object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
