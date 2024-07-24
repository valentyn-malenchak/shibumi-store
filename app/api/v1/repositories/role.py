"""Module that contains role repository class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
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
        """Returns a query filter for list of roles.

        Args:
            _ (Any): Parameters for list searching.
            __ (Any): Parameters for list filtering.

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

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> Mapping[str, Any]:
        """
        Updates and retrieves a single role from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update role.

        Returns:
            Mapping[str, Any]: The retrieved role.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(
        self, *, session: AsyncIOMotorClientSession | None = None, **fields: Any
    ) -> Any:
        """Creates a new role in repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): The fields for the new role.

        Returns:
            Any: The ID of created role.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> None:
        """Updates a role in repository.

        Args:
            id_ (ObjectId): The unique identifier of the role.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update role.

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
