"""Contains MongoDB client."""


from injector import inject
from motor.motor_asyncio import AsyncIOMotorClient

from app.settings import SETTINGS
from app.utils.metas import SingletonMeta


@inject
class MongoDBClient(metaclass=SingletonMeta):
    """MongoDB client singleton."""

    def __init__(self) -> None:
        """Initialize MongoDB client."""

        self._client: AsyncIOMotorClient = AsyncIOMotorClient(
            f"mongodb://{SETTINGS.MONGODB_USER}:{SETTINGS.MONGODB_PASSWORD}"
            f"@{SETTINGS.MONGODB_HOST}:{SETTINGS.MONGODB_PORT}/"
            f"?authMechanism=SCRAM-SHA-256"
        )

    @property
    def client(self) -> AsyncIOMotorClient:
        """Mongo client getter."""
        return self._client

    def close(self) -> None:
        """Closes MongoDB client."""
        self._client.close()

    @classmethod
    def get_instance(cls) -> "MongoDBClient":
        """Gets MongoDB client instance."""
        return cls()
