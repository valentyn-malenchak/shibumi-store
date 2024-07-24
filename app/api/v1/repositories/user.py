"""Module that contains user repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo.errors import DuplicateKeyError

from app.api.v1.repositories import BaseRepository
from app.exceptions import EntityDuplicateKeyError
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
        """Returns a query filter for list of users.

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
        """Returns a query projection for list of users.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """
        return None

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of users.

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
        Updates and retrieves a single user from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update user.

        Returns:
            Mapping[str, Any]: The retrieved user.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": {**fields, "updated_at": arrow.utcnow().datetime}},
            session=session,
        )

    async def create(
        self, *, session: AsyncIOMotorClientSession | None = None, **fields: Any
    ) -> Any:
        """Creates a new user in repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): The fields for the new user.

        Returns:
            Any: The ID of created user.

        """

        try:
            return await self._mongo_service.insert_one(
                collection=self._collection_name,
                document={
                    **fields,
                    "email_verified": False,
                    "deleted": False,
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                session=session,
            )

        except DuplicateKeyError:
            raise EntityDuplicateKeyError

    async def update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> None:
        """Updates a user in repository.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update category.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": {**fields, "updated_at": arrow.utcnow().datetime}},
            session=session,
        )
