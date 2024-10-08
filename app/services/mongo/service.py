"""Module that contains MongoDB service."""

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from fastapi import Depends
from injector import inject
from mongodb_migrations.cli import MigrationManager
from mongodb_migrations.config import Configuration, Execution
from motor.motor_asyncio import (
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from pymongo import ReturnDocument

from app.services.base import BaseService
from app.services.mongo.client import MongoDBClient
from app.settings import SETTINGS


@inject
class MongoDBService(BaseService):
    """MongoDB service facade."""

    _name: str = "mongo_db"

    def __init__(self, mongo_client: MongoDBClient = Depends()) -> None:
        """MongoDB service initialization method.

        Args:
            mongo_client (MongoDBClient): MongoDB client.

        """

        self._db: AsyncIOMotorDatabase = mongo_client.client[SETTINGS.MONGODB_NAME]

    @staticmethod
    def run_migrations(upgrade: bool = True, to_datetime: str | None = None) -> None:
        """Runs MongoDB migrations.

        Args:
            upgrade (bool): Defines type of migration (upgrade or downgrade).
            Default to True.
            to_datetime (str | None): Defines a prefix of migration upgrade/downgrade
            operations will reach.

        """

        config = Configuration(
            {
                "mongo_url": (
                    f"mongodb://{SETTINGS.MONGODB_HOST}:{SETTINGS.MONGODB_PORT}/"
                    f"{SETTINGS.MONGODB_NAME}?authSource={SETTINGS.MONGO_AUTH_SOURCE}",
                ),
                "mongo_database": SETTINGS.MONGODB_NAME,
                "mongo_username": SETTINGS.MONGODB_USER,
                "mongo_password": SETTINGS.MONGODB_PASSWORD,
                "execution": Execution.MIGRATE
                if upgrade is True
                else Execution.DOWNGRADE,
                "to_datetime": to_datetime,
            }
        )

        manager = MigrationManager(config)

        manager.run()

    def _get_collection_by_name(self, collection: str) -> AsyncIOMotorCollection:
        """Fetches collection by name.

        Args:
            collection (str): Collection name.

        Returns:
            AsyncIOMotorCollection: Collection object.

        Raises:
            NotInitializedDBError: if MongoDB is not initialized.

        """
        return self._db[collection]

    async def find(  # noqa: PLR0913
        self,
        collection: str,
        skip: int | None = None,
        limit: int | None = None,
        filter_: Mapping[str, Any] | None = None,
        projection: Mapping[str, Any] | None = None,
        sort: Sequence[tuple[str, int | str | Mapping[str, Any]]] | None = None,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Mapping[str, Any]]:
        """
        Finds documents that satisfy the specified query criteria in the chosen
        collection.

        Args:
            collection (str): Collection name.
            skip (int): The number of documents to skip in the results set.
            Defaults to None.
            limit (int): Specifies the maximum number of documents will be
            returned. Defaults to None.
            filter_ (Mapping[str, Any] | None): Specifies query selection
            criteria. Defaults to None.
            projection (Mapping[str, Any] | None): Specifies list of field names that
            should be returned in the result set or a dict specifying the fields
            to include or exclude. Defaults to None.
            sort (Sequence[tuple[str, int | str | Mapping[str, Any]]] | None):
            Specifies the order in which the query returns matching documents.
            Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            list[Mapping[str, Any]]: List of documents.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        cursor = collection_.find(
            filter=filter_, projection=projection, session=session
        )

        if sort is not None:
            cursor = cursor.sort(sort)

        if skip is not None:
            cursor = cursor.skip(skip)

        if limit is not None:
            cursor = cursor.limit(limit)

        return await cursor.to_list(length=limit)

    async def count_documents(
        self,
        collection: str,
        filter_: Mapping[str, Any] | None = None,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Counts documents in the chosen collection.

        Args:
            collection (str): Collection name.
            filter_ (Mapping[str, Any] | None): Specifies query selection
            criteria. Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            int: Count of documents.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        return (
            await collection_.count_documents(filter=filter_, session=session)
            if filter_ is not None
            else await collection_.count_documents(filter={}, session=session)
        )

    async def distinct(
        self,
        collection: str,
        field: str,
        filter_: Mapping[str, Any] | None = None,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Any]:
        """Finds the distinct values for a specified field across chosen collection and
        returns the results in an array.

        Args:
            collection (str): Collection name.
            field (str): The field for which to return distinct values.
            filter_ (Mapping[str, Any] | None): Specifies query selection
            criteria. Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            list[Any]: List of distinct values.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        return await collection_.distinct(field, filter=filter_, session=session)

    async def find_one(
        self,
        collection: str,
        filter_: Mapping[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any] | None:
        """
        Finds one document that satisfies the specified query criteria in the chosen
        collection.

        Args:
            collection (str): Collection name.
            filter_ (Mapping[str, Any]): Specifies query selection criteria.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: Document or None.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        return await collection_.find_one(filter=filter_, session=session)

    async def find_one_and_update(  # noqa: PLR0913
        self,
        collection: str,
        filter_: Mapping[str, Any],
        update: Mapping[str, Any],
        upsert: bool = False,
        return_updated: bool = True,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any]:
        """Updates a document in the chosen collection and return it.

        Args:
            collection (str): Collection name.
            filter_ (Mapping[str, Any]): Specifies query selection criteria.
            update (Mapping[str, Any]): Data to be updated.
            upsert (bool): Use update or insert. Defaults to False.
            return_updated (bool): Defines if method should return document after
            the update or original version. Defaults to True (updated document).
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None:

        """

        collection_ = self._get_collection_by_name(collection=collection)

        return await collection_.find_one_and_update(
            filter=filter_,
            update=update,
            upsert=upsert,
            return_document=ReturnDocument.AFTER
            if return_updated is True
            else ReturnDocument.BEFORE,
            session=session,
        )

    async def insert_one(
        self,
        collection: str,
        document: Mapping[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Inserts a document in the chosen collection.

        Args:
            collection (str): Collection name.
            document (Mapping[str, Any]): Document to be
            inserted in collection.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created document.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        result = await collection_.insert_one(document=document, session=session)

        return result.inserted_id

    async def insert_many(
        self,
        collection: str,
        documents: Iterable[Mapping[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Any]:
        """Inserts multiple documents in bulk in the chosen collection.

        Args:
            collection (str): Collection name.
            documents (Iterable[Mapping[str, Any]]): Documents to be
            inserted in collection.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            list[Any]: The IDs of created documents.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        result = await collection_.insert_many(documents=documents, session=session)

        return result.inserted_ids

    async def update_one(
        self,
        collection: str,
        filter_: Mapping[str, Any],
        update: Mapping[str, Any],
        upsert: bool = False,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a document in the chosen collection.

        Args:
            collection (str): Collection name.
            filter_ (Mapping[str, Any]): Specifies query selection criteria.
            update (Mapping[str, Any]): Data to be updated.
            upsert (bool): Use update or insert. Defaults to False.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        await collection_.update_one(
            filter=filter_, update=update, upsert=upsert, session=session
        )

    async def delete_one(
        self,
        collection: str,
        filter_: Mapping[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Deletes a document in the chosen collection.

        Args:
            collection (str): Collection name.
            filter_ (Mapping[str, Any]): Specifies query selection criteria.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        await collection_.delete_one(filter=filter_, session=session)

    async def delete_many(
        self, collection: str, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes multiple documents from the chosen collection.

        Args:
            collection (str): Collection name.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        await collection_.delete_many(filter={}, session=session)

    async def aggregate(
        self,
        collection: str,
        pipeline: Sequence[Mapping[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
        cursor_length: int | None = None,
    ) -> list[Mapping[str, Any]]:
        """
        Aggregates a pipeline in the chosen collection.

        Args:
            collection (str): Collection name.
            pipeline (Mapping[str, Any]): A single command or list of
            aggregation commands.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            cursor_length (int | None): Count of documents will be returned by cursor.
            Defaults to None.

        Returns:
            list[Mapping[str, Any]]: List of documents.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        cursor = collection_.aggregate(pipeline=pipeline, session=session)

        return await cursor.to_list(length=cursor_length)
