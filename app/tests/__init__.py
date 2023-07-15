"""Module that contains base test component."""

from fastapi.testclient import TestClient

from app.app import app


class BaseTest:
    """Test class for API endpoints in the FastAPI application."""

    _client = None

    @property
    def client(self):
        """
        Get the TestClient instance for the FastAPI application.

        If the TestClient instance is not created yet, it is lazily created.

        Returns:
            TestClient: The TestClient instance for the FastAPI application.

        """

        if self._client is None:
            self._client = TestClient(app.api)

        return self._client
