"""Module that contains tests for thread routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.constants import (
    AppConstants,
    HTTPErrorMessagesEnum,
)
from app.services.mongo.constants import MongoCollectionsEnum
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    CUSTOMER_USER,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestThread(BaseAPITest):
    """Test class for thread APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.THREADS,
            )
        ],
        indirect=True,
    )
    async def test_get_thread(self, test_client: AsyncClient, arrange_db: None) -> None:
        """Test get thread."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "6669b5634cef83e11dbc7abf",
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.THREADS,)],
        indirect=True,
    )
    async def test_get_thread_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread in case there is no token."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "6669b5634cef83e11dbc7abf",
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_thread_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread in case user does not have appropriate scope."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_thread_user_thread_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread in case thread is not found."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Thread")
        }
