"""Module that contains tests for health routes."""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.tests.api_v1 import BaseTest


class TestHealth(BaseTest):
    """Test class for health API endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    async def test_get_health(self, test_client: AsyncClient) -> None:
        """Test case for the GET health endpoint."""
        response = await test_client.get("/health/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
