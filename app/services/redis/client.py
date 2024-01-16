"""Contains Redis client."""

from redis import StrictRedis

from app.services.base import BaseClient
from app.settings import SETTINGS


class RedisClient(BaseClient):
    """Redis client."""

    _client = StrictRedis(
        host=SETTINGS.REDIS_HOST,
        port=SETTINGS.REDIS_PORT,
        password=SETTINGS.REDIS_PASSWORD,
        decode_responses=True,
    )

    @property
    def client(self) -> StrictRedis:
        """Redis client getter."""
        return self._client

    @classmethod
    def close(cls) -> None:
        """Closes Redis client."""
        if cls._client is not None:
            cls._client.close()  # type: ignore
