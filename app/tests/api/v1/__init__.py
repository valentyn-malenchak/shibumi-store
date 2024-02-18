"""Module that contains base API test component."""

import asyncio
from typing import Any, AsyncGenerator, Generator
from unittest.mock import patch

import pytest
import pytest_asyncio
from _pytest.fixtures import SubRequest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.app import app
from app.loaders import JSONFileLoader
from app.tests import BaseTest
from app.tests.fixtures.manager import FileFixtureManager


class BaseAPITest(BaseTest):
    """Test class for API endpoints of FastAPI application."""

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
    async def arrange_db(
        self, request: SubRequest, set_event_loop: None
    ) -> AsyncGenerator[None, None]:
        """Loads and clears data in DB before and after acting unit test.

        Args:
            request (SubRequest): Fixture request.
            set_event_loop (None.): Event loop fixture.

        """

        file_fixture_manager = FileFixtureManager(collection_names=request.param)

        await file_fixture_manager.clear()

        await file_fixture_manager.load()

        yield

        await file_fixture_manager.clear()
