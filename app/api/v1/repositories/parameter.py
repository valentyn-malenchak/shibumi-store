"""Module that contains parameter repository class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum


class ParameterRepository(BaseRepository):
    """Parameter repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.PARAMETERS

    @staticmethod
    async def _get_list_query_filter(*_: Any, **__: Any) -> Mapping[str, Any]:
        """Returns a query filter for list of parameters.

        Args:
            _ (Any): Parameters for list searching.
            __ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        """
        return {}

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list of parameters.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return {
            "_id": ProjectionValuesEnum.EXCLUDE,
            "machine_name": ProjectionValuesEnum.INCLUDE,
            "type": ProjectionValuesEnum.INCLUDE,
        }

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of parameters.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        """
        return None

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Retrieves a parameter from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the parameter.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved parameter object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """
        Updates and retrieves a single parameter from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the parameter.
            data (Any): Data to update parameter.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved parameter object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(
        self,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Creates a new parameter in repository.

        Args:
            data (Any): The data for the new parameter.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(
        self,
        id_: ObjectId,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a parameter in repository.

        Args:
            id_ (ObjectId): The unique identifier of the parameter.
            data (Any): Data to update parameter.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
