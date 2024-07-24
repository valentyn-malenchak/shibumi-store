"""App level unit tests."""

from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.app import app
from app.constants import AppConstants
from app.tests import BaseTest


class TestApp(BaseTest):
    """Test class for application level unit tests."""

    @patch("uvicorn.run")
    def test_application_runs_server(self, uvicorn_run_mock: MagicMock) -> None:
        """Test application 'run' method runs uvicorn."""

        app.run()

        assert uvicorn_run_mock.call_count == 1

    @patch("motor.motor_asyncio.AsyncIOMotorClient.close")
    @patch("redis.StrictRedis.close")
    def test_application_events(
        self, mongo_client_close_mock: MagicMock, redis_client_close_mock: MagicMock
    ) -> None:
        """Test application startup and shutdown events."""

        with TestClient(app) as client:
            response = client.get(f"{AppConstants.API_V1_PREFIX}/health/")

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        assert mongo_client_close_mock.call_count == 1
        assert redis_client_close_mock.call_count == 1
