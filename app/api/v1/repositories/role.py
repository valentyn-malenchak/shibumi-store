"""Module that contains role repository class."""

from collections.abc import Mapping
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.constants import RolesEnum
from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum


class RoleRepository(BaseRepository):
    """Role repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.ROLES

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
        return {"scopes": ProjectionValuesEnum.EXCLUDE}

    async def get_scopes_by_roles(
        self,
        roles: list[RolesEnum],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[str]:
        """Retrieves a list of scopes from the repository by roles name list.

        Args:
            roles (list[str]): List of roles.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            list[str]: The retrieved scopes.

        """

        scopes = await self._mongo_service.aggregate(
            collection=self._collection_name,
            pipeline=[
                {"$match": {"machine_name": {"$in": roles}}},
                {"$unwind": "$scopes"},
                {"$group": {"_id": "$scopes"}},
            ],
            session=session,
        )

        return [scope["_id"] for scope in scopes]
