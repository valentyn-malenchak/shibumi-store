"""Module that contains tests for health routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.constants import HTTPErrorMessagesEnum
from app.services.mongo.constants import MongoCollectionsEnum
from app.settings import SETTINGS
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import SHOP_SIDE_USER, TEST_JWT, USER_NO_SCOPES


class TestHealth(BaseAPITest):
    """Test class for health API endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_get_health(self, test_client: AsyncClient, db: None) -> None:
        """Test get application health."""
        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/health/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_get_health_no_scope(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test get application health in case user does not have appropriate scope."""
        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/health/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}
