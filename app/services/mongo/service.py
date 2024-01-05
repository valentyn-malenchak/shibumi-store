"""Module that contains MongoDB service."""

from typing import Any, Iterable, List, Mapping, Sequence

from fastapi import Depends
from injector import inject
from motor.motor_asyncio import (
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from app.services.base import BaseService
from app.services.mongo.client import MongoDBClient
from app.settings import SETTINGS


@inject
class MongoDBService(BaseService):
    """MongoDB service facade."""

    _name: str = "mongo_db"

    def __init__(self, mongo_client: MongoDBClient = Depends(MongoDBClient)) -> None:
        """MongoDB service initialization method.

        Args:
            mongo_client (MongoDBClient): MongoDB client.

        """

        self._db: AsyncIOMotorDatabase = mongo_client.client[SETTINGS.MONGODB_NAME]

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

    async def find_one(
        self,
        collection: str,
        filter_: Mapping[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any] | None:
        """
        Finds one document that satisfies the specified query
        criteria on chosen the collection.

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

    async def insert_one(
        self,
        collection: str,
        document: Mapping[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Inserts a document for chosen collection.

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
    ) -> List[Any]:
        """Inserts multiple documents in bulk for chosen collection.

        Args:
            collection (str): Collection name.
            documents (Iterable[Mapping[str, Any]]): Documents to be
            inserted in collection.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The IDs of created documents.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        result = await collection_.insert_many(documents=documents, session=session)

        return result.inserted_ids

    async def update_one(
        self,
        collection: str,
        filter_: Mapping[str, Any],
        update: Mapping[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a document for chosen collection.

        Args:
            collection (str): Collection name.
            filter_ (Mapping[str, Any]): Specifies query selection criteria.
            update (Mapping[str, Any]): Data to be updated.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        await collection_.update_one(filter=filter_, update=update, session=session)

    async def delete_many(
        self, collection: str, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all documents from collection.

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
    ) -> List[Mapping[str, Any]]:
        """
        Aggregates a pipeline on chosen collection.

        Args:
            collection (str): Collection name.
            pipeline (Mapping[str, Any]): A single command or list of
            aggregation commands.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            cursor_length (int | None): Count of documents will be returned by cursor.
            Defaults to None.

        Returns:
            List[Mapping[str, Any]]: List of documents.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        cursor = collection_.aggregate(pipeline=pipeline, session=session)

        return await cursor.to_list(length=cursor_length)
