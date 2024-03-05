"""Module that contains product repository class."""

from typing import Any, Dict, List, Mapping

from bson import ObjectId
from fastapi import Depends
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.constants import ProductParameterTypesEnum
from app.api.v1.repositories import BaseRepository
from app.api.v1.repositories.category import CategoryRepository
from app.constants import HTTPErrorMessagesEnum, ProjectionValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum
from app.services.mongo.service import MongoDBService


@inject
class ProductRepository(BaseRepository):
    """Product repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.PRODUCTS

    def __init__(
        self,
        mongo_service: MongoDBService = Depends(),
        category_repository: CategoryRepository = Depends(),
    ) -> None:
        """Initializes the ProductRepository.

        This method sets up the MongoDB service instance for data access.

        Args:
            mongo_service (MongoDBService): An instance of the MongoDB service.
            category_repository (CategoryRepository): Category repository.

        """

        super().__init__(mongo_service=mongo_service)

        self.category_repository = category_repository

    @staticmethod
    async def _get_list_query_filter(
        search: str | None,
        category_id: ObjectId | None = None,
        available: bool | None = None,
        parameters: Dict[str, List[Any]] | None = None,
        **_: Any,
    ) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            search (str | None): Parameters for list searching.
            category_id (ObjectId | None): Category identifier. Defaults to None.
            available (bool | None): Available products filter. Defaults to None.
            parameters (Dict[str, List[Any]] | None): Product parameters filter.
            Defaults to None.
            _ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter: Dict[str, Any] = {}

        if search is not None:
            query_filter["$text"] = {"$search": search}

        if category_id is not None:
            query_filter["category_id"] = category_id

        if available is not None:
            query_filter["available"] = available

        if parameters:
            for name, values in parameters.items():
                query_filter[f"parameters.{name}"] = (
                    values[0] if len(values) == 1 else {"$in": values}
                )

        return query_filter

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """

        return {
            "description": ProjectionValuesEnum.EXCLUDE,
            "html_body": ProjectionValuesEnum.EXCLUDE,
            "parameters": ProjectionValuesEnum.EXCLUDE,
        }

    async def calculate_product_parameters_values_by_category(
        self,
        category_id: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Calculates list of values for specific product category parameter.

        Args:
            category_id (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            ValueError: If category with id does not exist.

        """

        category = await self.category_repository.get_by_id(
            id_=category_id, session=session
        )

        if category is None:
            raise ValueError(
                HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.value.format(
                    entity="Category"
                )
            )

        parameters = category["parameters"]

        pipeline: List[Dict[str, Any]] = [{"$match": {"category_id": category_id}}]

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

        if result is not None:
            parameters_values = {
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

            await self._mongo_service.update_one(
                collection=MongoCollectionsEnum.PARAMETERS_VALUES,
                filter_={"_id": parameters_values["_id"]},
                update={"$set": parameters_values},
                upsert=True,
                session=session,
            )
