"""Module that contains role scopes repository class."""

from typing import Any, Dict, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


class RoleScopesRepository(BaseRepository):
    """Role-scopes repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.ROLES_SCOPES.value

    async def get_item_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Retrieves a role-scopes from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role-scopes.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved role-scopes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_scopes_by_roles(
        self, roles: List[str], *, session: AsyncIOMotorClientSession | None = None
    ) -> List[str]:
        """Retrieves a list of scopes from the repository by roles name list.

        Args:
            roles (List[str]): List of roles.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[str]: The retrieved scopes.

        """

        scopes = await self._mongo_service.aggregate(
            collection=self._collection_name,
            pipeline=[
                {"$match": {"role": {"$in": roles}}},
                {"$unwind": "$scopes"},
                {"$group": {"_id": "$scopes"}},
            ],
            session=session,
        )

        return [scope["_id"] for scope in scopes]

    async def create_item(
        self, item: Any, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Create a new role-scopes in repository.

        Args:
            item (Any): The data for the new role-scopes.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created role-scopes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create_items(
        self,
        items: List[Dict[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Any]:
        """Creates bulk roles-scopes in the repository.

        Args:
            items (List[Dict[str, Any]]): Roles-scopes to be created.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The IDs of created roles-scopes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_all_items(
        self, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all roles-scopes from the repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_item_by_id(
        self,
        id_: ObjectId,
        item: Dict[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a role-scopes in repository.

        Args:
            id_ (ObjectId): The unique identifier of the role-scopes.
            item (Any): Data to update role-scopes.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
