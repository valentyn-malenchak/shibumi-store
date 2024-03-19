"""Module that contains user repository class."""

from collections.abc import Mapping
from typing import Any

from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


@inject
class UserRepository(BaseRepository):
    """User repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.USERS

    @staticmethod
    async def _get_list_query_filter(
        search: str | None,
        roles: list[str] | None = None,
        deleted: bool | None = None,
        **_: Any,
    ) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            search (str | None): Parameters for list searching.
            roles (list[str] | None): List of roles for filtering. Defaults to None.
            deleted (bool | None): Deleted status filtering. Defaults to None.
            _ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter: dict[str, Any] = {}

        if search is not None:
            query_filter["$text"] = {"$search": search}

        if roles:
            query_filter["roles"] = {"$in": roles}

        if deleted is not None:
            query_filter["deleted"] = deleted

        return query_filter

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return None

    @staticmethod
    def get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns list default sorting.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        """
        return None

    async def get_by_username(
        self, username: str, *, session: AsyncIOMotorClientSession | None = None
    ) -> Mapping[str, Any] | None:
        """Retrieves a user from the repository by its username.

        Args:
            username (str): Username.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: User document or None.

        """

        return await self._mongo_service.find_one(
            collection=self._collection_name,
            filter_={"username": username},
            session=session,
        )
