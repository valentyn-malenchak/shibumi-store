"""Module that contains role repository class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.constants import RolesEnum
from app.api.v1.models import Search
from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum


class RoleRepository(BaseRepository):
    """Role repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.ROLES

    async def _get_list_query_filter(
        self, filter_: Any, search: Search | None
    ) -> Mapping[str, Any]:
        """Returns a query filter for list of roles.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search | None): Parameters for list searching.

        Returns:
            (Mapping[str, Any]): List query filter.

        """
        return {}

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list of roles.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return {"scopes": ProjectionValuesEnum.EXCLUDE}

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of roles.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        """
        return None

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Retrieves a role from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved role object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """
        Updates and retrieves a single role from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role.
            data (Any): Data to update role.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved role object.

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
        """Creates a new role in repository.

        Args:
            data (Any): The data for the new role.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created role.

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
        """Updates a role in repository.

        Args:
            id_ (ObjectId): The unique identifier of the role.
            data (Any): Data to update role.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

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
