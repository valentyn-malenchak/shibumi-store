"""Module that contains base API test component."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import arrow
import pytest
import pytest_asyncio
from _pytest.fixtures import SubRequest
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.app import app
from app.tests import BaseTest
from app.tests.constants import FROZEN_DATETIME
from app.tests.fixtures.manager import FileFixtureManager


class BaseAPITest(BaseTest):
    """Test class for API endpoints of FastAPI application."""

    _client = None
    _APP_BASE_URL = "http://test"

    @pytest_asyncio.fixture(loop_scope="session")
    async def test_client(self) -> AsyncGenerator[AsyncClient, None]:
        """Opens the TestClient generator for the FastAPI application."""
        async with AsyncClient(
            transport=ASGITransport(app), base_url=self._APP_BASE_URL
        ) as client:
            yield client

    @pytest.fixture(scope="session", autouse=True)
    def event_loop_mock(self) -> Generator[None, None, None]:
        """Fixture that sets MongoDB client event loop."""

        with patch.object(
            AsyncIOMotorClient, "get_io_loop", new=asyncio.get_running_loop
        ):
            yield

    @pytest.fixture
    def datetime_now_mock(self) -> Generator[MagicMock, None, None]:
        """Arrow datetime now mock."""

        with patch("arrow.utcnow") as mock:
            mock.return_value = arrow.get(FROZEN_DATETIME)

            yield mock

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
    def redis_setex_mock(self) -> Generator[AsyncMock, None, None]:
        """Redis setex operation mock."""

        with patch("redis.asyncio.Redis.setex", new=AsyncMock()) as mock:
            yield mock

    @pytest.fixture
    def redis_get_mock(self, request: SubRequest) -> Generator[AsyncMock, None, None]:
        """Redis get operation mock."""

        with patch("redis.asyncio.Redis.get", new=AsyncMock()) as mock:
            mock.return_value = getattr(request, "param", None)

            yield mock

    @pytest.fixture
    def redis_delete_mock(self) -> Generator[AsyncMock, None, None]:
        """Redis delete operation mock."""

        with patch("redis.asyncio.Redis.delete", new=AsyncMock()) as mock:
            yield mock

    @pytest_asyncio.fixture
    async def db(
        self, request: SubRequest, event_loop_mock: None
    ) -> AsyncGenerator[None, None]:
        """Loads and clears data in DB before and after acting unit test.

        Args:
            request (SubRequest): Fixture request.
            event_loop_mock (None): Event loop fixture.

        """

        file_fixture_manager = FileFixtureManager(
            collection_names=getattr(request, "param", None)
        )

        await file_fixture_manager.clear()

        await file_fixture_manager.load()

        yield

        await file_fixture_manager.clear()
