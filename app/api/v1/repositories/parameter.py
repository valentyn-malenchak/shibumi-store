"""Module that contains parameter repository class."""

from collections.abc import Mapping
from typing import Any

from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum


class ParameterRepository(BaseRepository):
    """Parameter repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.PARAMETERS

    @staticmethod
    async def _get_list_query_filter(*_: Any, **__: Any) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            _ (Any): Parameters for list searching.
            __ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        """
        return {}

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return {
            "_id": ProjectionValuesEnum.EXCLUDE,
            "machine_name": ProjectionValuesEnum.INCLUDE,
            "type": ProjectionValuesEnum.INCLUDE,
        }

    @staticmethod
    def get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns list default sorting.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        """
        return None
