"""Module that contains MongoDB service."""

from typing import Any, List

from motor.motor_asyncio import AsyncIOMotorClient

from app.exceptions import NotInitializedDBError
from app.services.base import BaseService
from app.settings import SETTINGS


class MongoDBService(BaseService):
    """MongoDB service facade."""

    _name: str = "mongo_db"
    _client = None
    _db = None

    @classmethod
    def on_startup(cls) -> None:
        """Runs on application startup."""
        mongodb_uri = (
            f"mongodb://{SETTINGS.MONGODB_USER}:{SETTINGS.MONGODB_PASSWORD}"
            f"@{SETTINGS.MONGODB_HOST}:{SETTINGS.MONGODB_PORT}/"
            f"?authMechanism=SCRAM-SHA-256"
        )

        cls._client = AsyncIOMotorClient(mongodb_uri)

        cls._db = cls._client[SETTINGS.MONGODB_NAME]

    @classmethod
    def on_shutdown(cls) -> None:
        """Runs on application shutdown."""
        if cls._client is not None:
            cls._client.close()

    async def get_collections(self) -> List[str]:
        """Fetches entities list from database.

        Raises:
            NotInitializedDBError: if MongoDB is not initialized.

        """
        if self._db is not None:
            return await self._db.list_collection_names()

        raise NotInitializedDBError

    def get_collection_by_name(self, collection: str) -> Any:
        """Fetches collection by name.

        Args:
            collection (str): Collection name.

        Raises:
            NotInitializedDBError: if MongoDB is not initialized.

        """
        if self._db is not None:
            return self._db[collection]

        raise NotInitializedDBError

    async def create_collection(self, name: str) -> Any:
        """Creates MongoDB collection in database.

        Args:
            name (str): Collection name.

        Raises:
            NotInitializedDBError: if MongoDB is not initialized.

        """
        if self._db is not None:
            return await self._db.create_collection(name)

        raise NotInitializedDBError
