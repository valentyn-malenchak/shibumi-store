"""Module that contains tests for thread routes."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.constants import (
    HTTPErrorMessagesEnum,
)
from app.services.mongo.constants import MongoCollectionsEnum
from app.settings import SETTINGS
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    CUSTOMER_USER,
    FROZEN_DATETIME,
    SHOP_SIDE_USER,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestThread(BaseAPITest):
    """Test class for thread APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.THREADS,
            )
        ],
        indirect=True,
    )
    async def test_get_thread(self, test_client: AsyncClient, db: None) -> None:
        """Test get thread."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "6669b5634cef83e11dbc7abf",
            "name": "ASUS TUF Gaming F15",
            "body": "Product discussion",
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "db",
        [(MongoCollectionsEnum.THREADS,)],
        indirect=True,
    )
    async def test_get_thread_no_token(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test get thread in case there is no token."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "6669b5634cef83e11dbc7abf",
            "name": "ASUS TUF Gaming F15",
            "body": "Product discussion",
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_get_thread_user_no_scope(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test get thread in case user does not have appropriate scope."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_get_thread_user_thread_is_not_found(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test get thread in case thread is not found."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Thread")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "db",
        [(MongoCollectionsEnum.USERS,)],
        indirect=True,
    )
    async def test_create_thread(
        self, test_client: AsyncClient, db: None, datetime_now_mock: MagicMock
    ) -> None:
        """Test create thread."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/",
            json={
                "name": "Thread name",
                "body": "Thread body!",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert self._exclude_fields(response.json(), exclude_keys=["id"]) == {
            "name": "Thread name",
            "body": "Thread body!",
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_thread_no_token(self, test_client: AsyncClient) -> None:
        """Test create thread in case there is no token."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/",
            json={
                "name": "Thread name",
                "body": "Thread body!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_create_thread_no_scope(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test create thread in case user does not have appropriate scope."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/",
            json={
                "name": "Thread name",
                "body": "Thread body!",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_create_thread_validate_data(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test create thread in case request data is invalid."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/",
            json={},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "name"], "Field required"),
            ("missing", ["body", "body"], "Field required"),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.THREADS)],
        indirect=True,
    )
    async def test_update_thread(
        self, test_client: AsyncClient, db: None, datetime_now_mock: MagicMock
    ) -> None:
        """Test update thread."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/66b729b027dcb71d3b8f0fe8/",
            json={
                "name": "New thread name",
                "body": "New thread body!",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "66b729b027dcb71d3b8f0fe8",
            "name": "New thread name",
            "body": "New thread body!",
            "created_at": "2024-08-10T09:45:00",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    async def test_update_thread_no_token(self, test_client: AsyncClient) -> None:
        """Test update thread in case there is no token."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/66b729b027dcb71d3b8f0fe8/",
            json={
                "name": "New thread name",
                "body": "New thread body!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_update_thread_no_scope(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test update thread in case user does not have appropriate scope."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/66b729b027dcb71d3b8f0fe8/",
            json={
                "name": "New thread name",
                "body": "New thread body!",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.THREADS)],
        indirect=True,
    )
    async def test_update_thread_validate_data(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test update thread in case request data is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/66b729b027dcb71d3b8f0fe8/",
            json={},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "name"], "Field required"),
            ("missing", ["body", "body"], "Field required"),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_update_thread_thread_is_not_found(
        self, test_client: AsyncClient, db: None
    ) -> None:
        """Test update thread in case thread is not found."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/threads/66b729b027dcb71d3b8f0fe8/",
            json={
                "name": "New thread name",
                "body": "New thread body!",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Thread")
        }
