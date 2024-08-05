"""Module that contains user repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo.errors import DuplicateKeyError

from app.api.v1.models import Search
from app.api.v1.models.user import User, UserCreateData, UserFilter, UserUpdateData
from app.api.v1.repositories import BaseRepository
from app.exceptions import EntityDuplicateKeyError
from app.services.mongo.constants import MongoCollectionsEnum


@inject
class UserRepository(BaseRepository):
    """User repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.USERS

    async def _get_list_query_filter(
        self, filter_: UserFilter, search: Search | None
    ) -> Mapping[str, Any]:
        """Returns a query filter for list of users.

        Args:
            filter_ (UserFilter): Parameters for list filtering.
            search (Search | None): Parameters for list searching.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter: dict[str, Any] = {}

        self._apply_list_search(query_filter=query_filter, search=search)

        if filter_.roles:
            query_filter["roles"] = {"$in": filter_.roles}

        if filter_.deleted is not None:
            query_filter["deleted"] = filter_.deleted

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

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> User:
        """Retrieves a user from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            User: The retrieved user object.

        """

        user = await self._get_one(_id=id_, session=session)

        return User(**user)

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: UserUpdateData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> User:
        """
        Updates and retrieves a single user from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            data (UserUpdateData): Data to update user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            User: The retrieved user object.

        """

        user = await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$set": {
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "patronymic_name": data.patronymic_name,
                    "email": data.email,
                    "phone_number": data.phone_number,
                    "birthdate": arrow.get(data.birthdate).datetime,
                    "roles": data.roles,
                    "email_verified": data.email_verified,
                    "updated_at": arrow.utcnow().datetime,
                }
            },
            session=session,
        )

        return User(**user)

    async def create(
        self,
        data: UserCreateData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Creates a new user in repository.

        Args:
            data (UserCreateData): The data for the new user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created user.

        """

        try:
            return await self._mongo_service.insert_one(
                collection=self._collection_name,
                document={
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "patronymic_name": data.patronymic_name,
                    "username": data.username,
                    "email": data.email,
                    "hashed_password": data.hashed_password,
                    "phone_number": data.phone_number,
                    "birthdate": arrow.get(data.birthdate).datetime,
                    "roles": data.roles,
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
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> None:
        """Updates a user in repository.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            data (Any): Data to update user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Softly deletes a user in repository.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": {"deleted": True, "updated_at": arrow.utcnow().datetime}},
            session=session,
        )

    async def get_by_username(
        self,
        username: str,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> User:
        """Retrieves a user from the repository by username.

        Args:
            username (str): Username.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            User: The retrieved user object.

        """

        user = await self._get_one(username=username, session=session)

        return User(**user)

    async def update_password(
        self,
        id_: ObjectId,
        hashed_password: str,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates user password.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            hashed_password (str): New hashed password.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$set": {
                    "hashed_password": hashed_password,
                    "updated_at": arrow.utcnow().datetime,
                }
            },
            session=session,
        )

    async def verify_email(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Verifies user email.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$set": {"email_verified": True, "updated_at": arrow.utcnow().datetime}
            },
            session=session,
        )
