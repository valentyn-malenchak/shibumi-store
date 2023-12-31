"""Contains MongoDB transaction manager."""

from typing import Any

from fastapi import Depends
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession

from app.services.mongo.client import MongoDBClient


@inject
class TransactionManager:
    """MongoDB transaction context manager."""

    def __init__(
        self, mongo_client: MongoDBClient = Depends(MongoDBClient.get_instance)
    ) -> None:
        """Transaction context manager initialization method.

        Args:
            mongo_client (MongoDBClient): MongoDB client.

        """

        self._client: AsyncIOMotorClient = mongo_client.client
        self._session: AsyncIOMotorClientSession | None = None

    async def __aenter__(self) -> AsyncIOMotorClientSession:
        """Starts a MongoDB transaction."""
        self._session = await self._client.start_session()
        self._session.start_transaction()
        return self._session

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Commits or aborts a transaction and finish the session."""

        if self._session is not None:
            if exc_type is not None:
                # An exception occurred, rollback the transaction
                await self._session.abort_transaction()
            else:
                # No exception, commit the transaction
                await self._session.commit_transaction()

            await self._session.end_session()
