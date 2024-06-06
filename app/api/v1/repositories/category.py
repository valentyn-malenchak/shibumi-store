"""Module that contains category repository class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.constants import ProductParameterTypesEnum
from app.api.v1.repositories import BaseRepository
from app.api.v1.repositories.category_parameters import CategoryParametersRepository
from app.constants import ProjectionValuesEnum, SortingValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum
from app.services.mongo.service import MongoDBService


class CategoryRepository(BaseRepository):
    """Category repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.CATEGORIES

    def __init__(
        self,
        mongo_service: MongoDBService = Depends(),
        category_parameters_repository: CategoryParametersRepository = Depends(),
    ) -> None:
        """Initializes the ProductRepository.

        This method sets up the MongoDB service instance for data access.

        Args:
            mongo_service (MongoDBService): An instance of the MongoDB service.
            category_parameters_repository (CategoryParametersRepository): Category
            parameters repository.

        """

        super().__init__(mongo_service=mongo_service)

        self.category_parameters_repository = category_parameters_repository

    async def _get_list_query_filter(
        self,
        *_: Any,
        path: str | None = None,
        leafs: bool = False,
        **__: Any,
    ) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            _ (Any): Parameters for list searching.
            path (str | None): Category tree path filtering. Defaults to None.
            leafs (bool): Defines if only leaf categories will be returned.
            Defaults to False.
            __ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter: dict[str, Any] = {}

        if path is not None:
            query_filter["path"] = {"$regex": f"^{path}"}

        if leafs is True:
            parent_ids = await self._mongo_service.distinct(
                self._collection_name, "parent_id", filter_={"parent_id": {"$ne": None}}
            )

            query_filter["_id"] = {"$nin": parent_ids}

        return query_filter

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return {"parameters": ProjectionValuesEnum.EXCLUDE}

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns list default sorting.

        Returns:
           list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        """
        return [("_id", SortingValuesEnum.ASC)]

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Mapping[str, Any] | None:
        """Retrieves a category with related data from the repository by its unique
        identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: The retrieved category.

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

        return result[0] if result else None

    async def get_one_and_update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> Mapping[str, Any]:
        """
        Updates and retrieves a single category from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update category.

        Returns:
            Mapping[str, Any]: The retrieved category.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(
        self, *, session: AsyncIOMotorClientSession | None = None, **fields: Any
    ) -> Any:
        """Creates a new category in repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): The fields for the new category.

        Returns:
            Any: The ID of created category.

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
        """Updates a category in repository.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            upsert (bool): Use update or insert. Defaults to False.
            fields (Any): Fields to update category.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": fields},
            upsert=upsert,
            session=session,
        )

    async def calculate_category_parameters(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Calculates list of parameters for specific product category.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        category = await self.get_by_id(id_=id_, session=session)

        # Ignore 'None' result from method, category is validated earlier
        parameters = category["parameters"]  # type: ignore

        pipeline: list[dict[str, Any]] = [{"$match": {"category_id": id_}}]

        list_type_parameters = [
            parameter
            for parameter in parameters
            if parameter["type"] == ProductParameterTypesEnum.LIST.name
        ]

        if list_type_parameters:
            pipeline.extend(
                [
                    {
                        "$unwind": {
                            "path": f"$parameters.{parameter['machine_name']}",
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
                        parameter["machine_name"]: {
                            "$addToSet": f"$parameters.{parameter['machine_name']}"
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

        category_parameters = {
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

        await self.category_parameters_repository.update_by_id(
            id_=category_parameters["_id"],
            upsert=True,
            session=session,
            **category_parameters,
        )

    async def get_category_parameters(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Mapping[str, Any] | None:
        """Retrieves parameters data from the repository by category identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: The retrieved parameters.

        """

        return await self.category_parameters_repository.get_by_id(
            id_=id_, session=session
        )
