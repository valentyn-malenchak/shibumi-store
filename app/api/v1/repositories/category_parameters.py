"""Module that contains category parameters repository class."""

from collections.abc import Mapping
from typing import Any

from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


class CategoryParametersRepository(BaseRepository):
    """Category parameters repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.CATEGORY_PARAMETERS

    @staticmethod
    async def _get_list_query_filter(*_: Any, **__: Any) -> Mapping[str, Any]:
        """Returns a query filter for list.

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
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
