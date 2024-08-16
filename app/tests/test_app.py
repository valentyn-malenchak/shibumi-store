"""App level unit tests."""

from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.app import app
from app.settings import SETTINGS
from app.tests import BaseTest


class TestApp(BaseTest):
    """Test class for application level unit tests."""

    @patch("uvicorn.run")
    def test_application_runs_server(self, uvicorn_run_mock: MagicMock) -> None:
        """Test application 'run' method runs uvicorn."""

        app.run()

        assert uvicorn_run_mock.call_count == 1

    @patch("mongodb_migrations.cli.MigrationManager.run")
    @patch("motor.motor_asyncio.AsyncIOMotorClient.close")
    @patch("redis.StrictRedis.close")
    def test_application_events(
        self,
        redis_client_close_mock: MagicMock,
        mongo_client_close_mock: MagicMock,
        mongo_migrations_run_mock: MagicMock,
    ) -> None:
        """Test application startup and shutdown events."""

        with TestClient(app) as client:
            # Migrations run on startup
            assert mongo_migrations_run_mock.call_count == 1

            response = client.get(f"{SETTINGS.APP_API_V1_PREFIX}/health/")

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Clients close on shutdown
        assert mongo_client_close_mock.call_count == 1
        assert redis_client_close_mock.call_count == 1
