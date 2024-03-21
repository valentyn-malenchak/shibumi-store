"""Module that contains base API test component."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from _pytest.fixtures import SubRequest
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.app import app
from app.tests import BaseTest
from app.tests.fixtures.manager import FileFixtureManager


class BaseAPITest(BaseTest):
    """Test class for API endpoints of FastAPI application."""

    _client = None
    _APP_BASE_URL = "http://test"

    @pytest_asyncio.fixture
    async def test_client(self) -> AsyncGenerator[AsyncClient, None]:
        """Opens the TestClient generator for the FastAPI application."""
        async with AsyncClient(
            transport=ASGITransport(app),  # type: ignore
            base_url=self._APP_BASE_URL,
        ) as client:
            yield client

    @pytest.fixture(scope="session", autouse=True)
    def set_event_loop(self) -> Generator[None, None, None]:
        """Fixture that sets MongoDB client event loop."""

        with patch.object(
            AsyncIOMotorClient, "get_io_loop", new=asyncio.get_running_loop
        ):
            yield

    @pytest.fixture
    def send_grid_send_mock(
        self, request: SubRequest
    ) -> Generator[MagicMock, None, None]:
        """SendGrid send operation mock."""

        with patch("sendgrid.SendGridAPIClient.send") as mock:
            param = getattr(request, "param", None)

            if isinstance(param, Exception):
                mock.side_effect = param
            else:
                mock.return_value = param

            yield mock

    @pytest.fixture
    def redis_setex_mock(self) -> Generator[MagicMock, None, None]:
        """Redis setex operation mock."""

        with patch("redis.Redis.setex") as mock:
            yield mock

    @pytest.fixture
    def redis_get_mock(self, request: SubRequest) -> Generator[MagicMock, None, None]:
        """Redis get operation mock."""

        with patch("redis.Redis.get") as mock:
            mock.return_value = getattr(request, "param", None)

            yield mock

    @pytest.fixture
    def redis_delete_mock(self) -> Generator[MagicMock, None, None]:
        """Redis delete operation mock."""

        with patch("redis.Redis.delete") as mock:
            yield mock

    @pytest_asyncio.fixture
    async def arrange_db(
        self, request: SubRequest, set_event_loop: None
    ) -> AsyncGenerator[None, None]:
        """Loads and clears data in DB before and after acting unit test.

        Args:
            request (SubRequest): Fixture request.
            set_event_loop (None.): Event loop fixture.

        """

        file_fixture_manager = FileFixtureManager(
            collection_names=getattr(request, "param", None)
        )

        await file_fixture_manager.clear()

        await file_fixture_manager.load()

        yield

        await file_fixture_manager.clear()
