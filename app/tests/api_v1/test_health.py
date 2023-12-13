"""Module that contains tests for health routes."""

from fastapi import status

from app.tests import BaseTest


class TestHealth(BaseTest):
    """Test class for health API endpoints in the FastAPI application."""

    def test_get_health(self) -> None:
        """Test case for the GET health endpoint."""
        response = self.client.get("/health/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
