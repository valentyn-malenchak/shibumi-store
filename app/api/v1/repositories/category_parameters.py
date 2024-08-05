"""Module that contains category parameters repository class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.models.category import CategoryParameters
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

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> CategoryParameters:
        """Retrieves a category-parameters from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category-parameters.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            CategoryParameters: The retrieved category-parameters object.

        """

        category_parameters = await self._get_one(_id=id_, session=session)

        return CategoryParameters(**category_parameters)

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """
        Updates and retrieves a single category-parameters from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category-parameters.
            data (Any): Data to update category-parameters.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved category-parameters object.

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
        """Creates a new category-parameter in repository.

        Args:
            data (Any): The data for the new category-parameters.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created category-parameter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(
        self,
        id_: ObjectId,
        data: dict[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
        upsert: bool = False,
    ) -> None:
        """Updates a category-parameters in repository.

        Args:
            id_ (ObjectId): The unique identifier of the category-parameters.
            data (dict[str, Any]): Data to update category-parameters.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            upsert (bool): Use update or insert. Defaults to False.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": data},
            upsert=upsert,
            session=session,
        )
