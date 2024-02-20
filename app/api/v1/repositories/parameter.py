"""Module that contains parameter repository class."""

from typing import Any, List, Mapping

from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum


class ParameterRepository(BaseRepository):
    """Parameter repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.PARAMETERS.value

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

    async def get(
        self,
        *_: Any,
        session: AsyncIOMotorClientSession | None = None,
        **__: Any,
    ) -> List[Mapping[str, Any]]:
        """Retrieves a list of parameters based on parameters.

        Args:
            _ (Any): Parameters for list searching, sorting and pagination.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            __ (Any): Parameters for list filtering.

        Returns:
            List[Mapping[str, Any]]: The retrieved list of parameters.

        """

        return await self._mongo_service.find(
            collection=self._collection_name,
            filter_={},
            projection=self._get_list_query_projection(),
            session=session,
        )

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return {
            "_id": ProjectionValuesEnum.EXCLUDE.value,
            "machine_name": ProjectionValuesEnum.INCLUDE.value,
            "type": ProjectionValuesEnum.INCLUDE.value,
        }
