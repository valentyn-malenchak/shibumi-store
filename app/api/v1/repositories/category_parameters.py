"""Module that contains category parameters repository class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


class CategoryParametersRepository(BaseRepository):
    """Category parameters repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.CATEGORY_PARAMETERS

    @staticmethod
    async def _get_list_query_filter(*_: Any, **__: Any) -> Mapping[str, Any]:
        """Returns a query filter for list of category-parameters.

        Args:
            _ (Any): Parameters for list searching.
            __ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list of category-parameters.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for category-parameters.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> Mapping[str, Any]:
        """
        Updates and retrieves a single category-parameter from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category-parameter.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update category-parameter.

        Returns:
            Mapping[str, Any]: The retrieved category-parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(
        self, *, session: AsyncIOMotorClientSession | None = None, **fields: Any
    ) -> Any:
        """Creates a new category-parameter in repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): The fields for the new category-parameter.

        Returns:
            Any: The ID of created category-parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        upsert: bool = False,
        **fields: Any,
    ) -> None:
        """Updates a category-parameter in repository.

        Args:
            id_ (ObjectId): The unique identifier of the category-parameter.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            upsert (bool): Use update or insert. Defaults to False.
            fields (Any): Fields to update category-parameter.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": fields},
            upsert=upsert,
            session=session,
        )
