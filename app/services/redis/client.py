"""Contains Redis client."""

from redis.asyncio import StrictRedis

from app.services.base import BaseClient
from app.settings import SETTINGS


class RedisClient(BaseClient):
    """Redis client."""

    _client: StrictRedis = StrictRedis(
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
    async def close(cls) -> None:
        """Closes Redis client."""
        await cls._client.aclose()
