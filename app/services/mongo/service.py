"""Module that contains MongoDB service."""

from typing import Any, Iterable, List, Mapping

from bson import ObjectId
from injector import inject
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.services.base import BaseService
from app.services.mongo.client import MongoDBClient
from app.settings import SETTINGS


@inject
class MongoDBService(BaseService):
    """MongoDB service facade."""

    _name: str = "mongo_db"

    def __init__(self) -> None:
        """MongoDB service initialization method."""

        mongo = MongoDBClient()
        self._db: AsyncIOMotorDatabase = mongo.client[SETTINGS.MONGODB_NAME]

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
        self, collection: str, filter_: Mapping[str, Any]
    ) -> Mapping[str, Any] | None:
        """
        Finds one document that satisfies the specified query
        criteria on chosen the collection.

        Args:
            collection (str): Collection name.
            filter_ (Mapping[str, Any]): Specifies query selection criteria.

        Returns:
            Mapping[str, Any] | None: Document or None.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        return await collection_.find_one(filter=filter_)

    async def insert_many(
        self, collection: str, documents: Iterable[Mapping[str, Any]]
    ) -> List[ObjectId]:
        """Inserts multiple documents in bulk for chosen collection.

        Args:
            collection (str): Collection name.
            documents (Iterable[Mapping[str, Any]]): Documents to be
            inserted in collection.

        Returns:
            List[ObjectId]: The IDs of created documents.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        result = await collection_.insert_many(documents=documents)

        return result.inserted_ids

    async def delete_many(self, collection: str) -> None:
        """Deletes all documents from collection.

        Args:
            collection (str): Collection name.

        """

        collection_ = self._get_collection_by_name(collection=collection)

        await collection_.delete_many({})
