"""Module that contains Redis service."""

from typing import Any

from fastapi import Depends

from app.services.base import BaseService
from app.services.redis.client import RedisClient


class RedisService(BaseService):
    """Redis service facade."""

    _name: str = "redis"

    def __init__(self, redis_client: RedisClient = Depends()) -> None:
        """Redis service initialization method.

        Args:
            redis_client (RedisClient): Redis client.

        """

        self._client = redis_client.client

    async def get(self, name: str) -> Any:
        """Returns value by name.

        Args:
            name: Name to find.

        Returns:
            Any: Value.

        """
        return await self._client.get(name)

    async def set(self, name: str, value: str, ttl: int) -> None:
        """Sets name-value pair with TTL into Redis.

        Args:
            name (str): Name to set.
            value (str): Value to set.
            ttl (int): Number of seconds the record will exist.

        """
        await self._client.setex(name=name, time=ttl, value=value)

    async def delete(self, name: str) -> None:
        """Deletes name-value pair by name.

        Args:
            name: Name to delete

        """
        await self._client.delete(name)
