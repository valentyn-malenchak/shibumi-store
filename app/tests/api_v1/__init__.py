"""Module that contains base test component."""

import asyncio
import os
from typing import Any, AsyncGenerator, Generator
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.v1.services.users import UserService
from app.app import app
from app.injector import injector
from app.loaders import JSONFileLoader


class BaseTest:
    """Test class for API endpoints in the FastAPI application."""

    _client = None
    _APP_BASE_URL = "http://test"

    @staticmethod
    def load_fixture(fixture_file_path: str) -> Any:
        """Loads data from fixture file.

        Args:
            fixture_file_path (str): Fixture file path.

        Returns:
            Any: Fixture content.

        """
        return JSONFileLoader(file_path=fixture_file_path).load()

    @pytest_asyncio.fixture
    async def test_client(self) -> AsyncGenerator[AsyncClient, None]:
        """Opens the TestClient generator for the FastAPI application."""
        async with AsyncClient(app=app, base_url=self._APP_BASE_URL) as client:
            yield client

    @pytest.fixture(scope="session", autouse=True)
    def set_event_loop(self) -> Generator[None, None, None]:
        """Fixture that sets MongoDB client event loop."""

        with patch.object(
            AsyncIOMotorClient, "get_io_loop", new=asyncio.get_running_loop
        ):
            yield

    @pytest_asyncio.fixture
    async def arrange_db(self, set_event_loop: None) -> AsyncGenerator[None, None]:
        """Loads data into DB before acting unit test."""

        service = injector.get(UserService)
        # Cleans users data before loading data to MongoDB
        await service.delete_all_items()

        # Loads users data
        fixture_file_path = os.path.join("app", "tests", "fixtures", "users.json")

        data = self.load_fixture(fixture_file_path)

        await service.create_items(data if isinstance(data, list) else [data])

        yield

        # Cleans users data
        await service.delete_all_items()
