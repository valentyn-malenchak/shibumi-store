"""Module that contains product repository class."""

from typing import Any, Dict, List, Mapping

from bson import ObjectId
from injector import inject

from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum


@inject
class ProductRepository(BaseRepository):
    """Product repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.PRODUCTS

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
