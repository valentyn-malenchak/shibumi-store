"""Module that contains category repository class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.constants import ProductParameterTypesEnum
from app.api.v1.models import Search
from app.api.v1.models.category import Category, CategoryFilter
from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum, SortingValuesEnum
from app.exceptions import EntityIsNotFoundError
from app.services.mongo.constants import MongoCollectionsEnum


class CategoryRepository(BaseRepository):
    """Category repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.CATEGORIES

    async def _get_list_query_filter(
        self, filter_: CategoryFilter, search: Search | None
    ) -> Mapping[str, Any]:
        """Returns a query filter for list of categories.

        Args:
            filter_ (CategoryFilter): Parameters for list filtering.
            search (Search | None): Parameters for list searching.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter: dict[str, Any] = {}

        if filter_.path is not None:
            query_filter["path"] = {"$regex": f"^{filter_.path}"}

        if filter_.leafs is True:
            parent_ids = await self._mongo_service.distinct(
                self._collection_name, "parent_id", filter_={"parent_id": {"$ne": None}}
            )

            query_filter["_id"] = {"$nin": parent_ids}

        return query_filter

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list of categories.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return {"parameters": ProjectionValuesEnum.EXCLUDE}

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of categories.

        Returns:
           list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        """
        return [("_id", SortingValuesEnum.ASC)]

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Category:
        """Retrieves a category with related data from the repository by its unique
        identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Category: The retrieved category object.

        Raises:
            EntityIsNotFoundError: In case category is not found.

        """

        result = await self._mongo_service.aggregate(
            collection=self._collection_name,
            pipeline=[
                {"$match": {"_id": id_}},
                {
                    "$lookup": {
                        "from": MongoCollectionsEnum.PARAMETERS,
                        "localField": "parameters",
                        "foreignField": "_id",
                        "as": "parameters",
                    }
                },
                {
                    "$lookup": {
                        "from": MongoCollectionsEnum.CATEGORIES,
                        "localField": "_id",
                        "foreignField": "parent_id",
                        "as": "children",
                    }
                },
                {"$addFields": {"has_children": {"$gt": [{"$size": "$children"}, 0]}}},
            ],
            session=session,
        )

        if not result:
            raise EntityIsNotFoundError

        return Category(**result[0])

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """
        Updates and retrieves a single category from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            data (Any): Data to update category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved category object.

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
        """Creates a new category in repository.

        Args:
            data (Any): The data for the new category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created category.

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
        """Updates a category in repository.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            data (Any): Data to update category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def calculate_category_parameters(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> dict[str, Any]:
        """Calculates list of parameters for specific product category.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            dict[str, Any]: The calculated category-parameters.

        """

        category = await self.get_by_id(id_=id_, session=session)

        # Ignore exception handling, category is validated earlier
        parameters = category.parameters

        pipeline: list[dict[str, Any]] = [{"$match": {"category_id": id_}}]

        list_type_parameters = [
            parameter
            for parameter in parameters
            if parameter.type == ProductParameterTypesEnum.LIST.name
        ]

        if list_type_parameters:
            pipeline.extend(
                [
                    {
                        "$unwind": {
                            "path": f"$parameters.{parameter.machine_name}",
                            "preserveNullAndEmptyArrays": True,
                        }
                    }
                    for parameter in list_type_parameters
                ]
            )

        pipeline.append(
            {
                "$group": {
                    "_id": "$category_id",
                    **{
                        parameter.machine_name: {
                            "$addToSet": f"$parameters.{parameter.machine_name}"
                        }
                        for parameter in parameters
                    },
                }
            },
        )

        result = await self._mongo_service.aggregate(
            collection=MongoCollectionsEnum.PRODUCTS,
            pipeline=pipeline,
            session=session,
        )

        return {
            parameter: sorted(
                value,
                # 'None' values will be in the end of list, not case-sensitive
                key=lambda element: (
                    element is None,
                    element.lower() if isinstance(element, str) else element,
                ),
            )
            if isinstance(value, list)
            else value
            for parameter, value in result[0].items()
        }
