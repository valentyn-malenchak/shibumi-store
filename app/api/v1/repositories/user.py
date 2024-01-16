"""Module that contains user repository class."""

from typing import Any, Dict, List, Mapping

from bson import ObjectId
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.models.user import User
from app.api.v1.repositories import BaseRepository
from app.constants import SortingTypesEnum
from app.services.mongo.constants import MongoCollectionsEnum


@inject
class UserRepository(BaseRepository):
    """User repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.USERS.value

    async def get(  # noqa: PLR0913
        self,
        search: str | None,
        sort_by: str | None,
        sort_order: SortingTypesEnum,
        page: int,
        page_size: int,
        *_: Any,
        roles: List[str] | None = None,
        deleted: bool | None = None,
    ) -> List[Mapping[str, Any]]:
        """Retrieves a list of users based on parameters.

        Args:
            search (str | None): Parameters for list searching.
            sort_by (str | None): Specifies a field for sorting.
            sort_order (SortingTypesEnum): Defines sort order - ascending or descending.
            page (int): Page number.
            page_size (int): Number of items on each page.
            _ (Any): Parameters for list filtering.
            roles (List[str] | None): List of roles for filtering. Defaults to None.
            deleted (bool | None): Deleted status filtering. Defaults to None.

        Returns:
            List[Mapping[str, Any]]: The retrieved list of users.

        """

        return await self._mongo_service.find(
            collection=self._collection_name,
            filter_=self._get_list_query_filter(
                search=search, roles=roles, deleted=deleted
            ),
            sort=self._get_list_sorting(sort_by=sort_by, sort_order=sort_order),
            skip=self._calculate_skip(page=page, page_size=page_size),
            limit=page_size,
        )

    @staticmethod
    def _get_list_query_filter(
        search: str | None,
        *_: Any,
        roles: List[str] | None = None,
        deleted: bool | None = None,
    ) -> Mapping[str, Any] | None:
        """Returns a list query filter.

        Args:
            search (str | None): Parameters for list searching.
            _ (Any): Parameters for list filtering.
            roles (List[str] | None): List of roles for filtering. Defaults to None.
            deleted (bool | None): Deleted status filtering. Defaults to None.

        Returns:
            (Mapping[str, Any] | None): List query filter.

        """

        query_filter = {
            "roles": {"$in": roles} if roles else None,
            "deleted": deleted,
            "$text": {"$search": search} if search else None,
        }

        return {key: value for key, value in query_filter.items() if value is not None}

    async def count(
        self,
        search: str | None,
        *_: Any,
        roles: List[str] | None = None,
        deleted: bool | None = None,
    ) -> int:
        """Counts documents based on parameters.

        Args:
            search (str | None): Parameters for list searching.
            _ (Any): Parameters for list filtering.
            roles (List[str] | None): List of roles for filtering. Defaults to None.
            deleted (bool | None): Deleted status filtering. Defaults to None.


        Returns:
            int: Count of documents.

        """
        return await self._mongo_service.count_documents(
            collection=self._collection_name,
            filter_=self._get_list_query_filter(
                search=search, roles=roles, deleted=deleted
            ),
        )

    async def get_by_id(
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

    async def get_by_username(
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

    async def create(
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

    async def create_many(
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

    async def update_by_id(
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

    async def delete_all(
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
