"""Module that contains base client and service classes."""

import abc
from typing import Any


class BaseClient(abc.ABC):
    """Base client class."""

    _client: Any = None

    @property
    @abc.abstractmethod
    def client(self) -> Any:
        """Client getter."""
        return self._client

    @classmethod
    @abc.abstractmethod
    async def close(cls) -> None:
        """Closes client."""
        raise NotImplementedError


class BaseService:
    """Base service class."""

    _name: str | None = None
