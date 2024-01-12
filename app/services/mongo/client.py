"""Contains MongoDB client."""

from motor.motor_asyncio import AsyncIOMotorClient

from app.settings import SETTINGS


class MongoDBClient:
    """MongoDB client."""

    _client = AsyncIOMotorClient(
        f"mongodb://{SETTINGS.MONGODB_USER}:{SETTINGS.MONGODB_PASSWORD}"
        f"@{SETTINGS.MONGODB_HOST}:{SETTINGS.MONGODB_PORT}/"
        f"?authMechanism=SCRAM-SHA-256&authSource={SETTINGS.MONGO_AUTH_SOURCE}"
    )

    @property
    def client(self) -> AsyncIOMotorClient:
        """Mongo client getter."""
        return self._client

    @classmethod
    def close(cls) -> None:
        """Closes MongoDB client."""
        if cls._client is not None:
            cls._client.close()
