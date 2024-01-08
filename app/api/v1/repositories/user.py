"""Module that contains user repository class."""

from typing import Any, Dict, List

from bson import ObjectId
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.models.user import User
from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


@inject
class UserRepository(BaseRepository):
    """User repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.USERS.value

    async def get_item_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> User | None:
        """Retrieves a user from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            User | None: User object or None.

        """

        user = await self._mongo_service.find_one(
            collection=self._collection_name, filter_={"_id": id_}, session=session
        )

        return User(**user) if user else None

    async def get_item_by_username(
        self, username: str, *, session: AsyncIOMotorClientSession | None = None
    ) -> User | None:
        """Retrieves a user from the repository by its username.

        Args:
            username (str): Username.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            User | None: User object or None.

        """

        user = await self._mongo_service.find_one(
            collection=self._collection_name,
            filter_={"username": username},
            session=session,
        )

        return User(**user) if user else None

    async def create_item(
        self, item: Dict[str, Any], *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Creates a new user in repository.

        Args:
            item (Dict[str, Any]): The data for the new item.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created user.

        """

        return await self._mongo_service.insert_one(
            collection=self._collection_name, document=item, session=session
        )

    async def create_items(
        self,
        items: List[Dict[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Any]:
        """Creates bulk users in the repository.

        Args:
            items (List[Dict[str, Any]]): Users to be created.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The IDs of created users.

        """

        return await self._mongo_service.insert_many(
            collection=self._collection_name,
            documents=items,
            session=session,
        )

    async def update_item_by_id(
        self,
        id_: ObjectId,
        item: Dict[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a user in repository.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            item (Dict[str, Any]): Data to update user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": item},
            session=session,
        )

    async def delete_all_items(
        self, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all users from the repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """
        await self._mongo_service.delete_many(
            collection=self._collection_name, session=session
        )
