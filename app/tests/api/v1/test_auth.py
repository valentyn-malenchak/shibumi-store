"""Module that contains tests for auth routes."""


from unittest.mock import Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from jose import ExpiredSignatureError

from app.api.v1.constants import ScopesEnum
from app.constants import HTTPErrorMessagesEnum
from app.services.mongo.constants import MongoCollectionsEnum
from app.tests.api.v1 import BaseTest
from app.tests.constants import FAKE_USER, JWT, USER, USER_NO_SCOPES


class TestAuth(BaseTest):
    """Test class for auth API endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_tokens(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test auth token creation."""

        response = await test_client.post(
            "/auth/tokens/",
            data={
                "username": "john.smith",
                "password": "john1234",
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert set(response.json().keys()) == {
            "access_token",
            "refresh_token",
            "token_type",
        }

    @pytest.mark.asyncio
    async def test_create_tokens_missing_fields(self, test_client: AsyncClient) -> None:
        """Test auth token creation in case username/password is missed."""

        response = await test_client.post(
            "/auth/tokens/",
            data={"username": "john.smith"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "grant_type"], "Field required"),
            ("missing", ["body", "password"], "Field required"),
        ]

    @pytest.mark.asyncio
    async def test_create_tokens_user_does_not_exist(
        self, test_client: AsyncClient
    ) -> None:
        """Test auth token creation in case user with such username does not exist."""

        response = await test_client.post(
            "/auth/tokens/",
            data={
                "username": "joe.smith",
                "password": "john1234",
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INCORRECT_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    async def test_create_tokens_invalid_password(
        self, test_client: AsyncClient
    ) -> None:
        """Test auth token creation in case user with such username does not exist."""

        response = await test_client.post(
            "/auth/tokens/",
            data={
                "username": "john.smith",
                "password": "john1234smith",
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INCORRECT_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_tokens_request_not_permitted_scopes(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test auth token creation in case user request not permitted scopes."""

        response = await test_client.post(
            "/auth/tokens/",
            data={
                "username": "john.smith",
                "password": "john1234",
                "scope": [
                    ScopesEnum.USERS_GET_ME.name,
                    ScopesEnum.HEALTH_GET_HEALTH.name,
                ],
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PERMISSION_DENIED.value
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    @patch("jose.jwt.decode", Mock(return_value=USER))
    async def test_refresh_access_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test refreshing access token."""

        response = await test_client.post(
            "/auth/access-token/", headers={"Authorization": f"Bearer {JWT}"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert set(response.json().keys()) == {"access_token", "token_type"}

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_token(
        self, test_client: AsyncClient
    ) -> None:
        """Test refreshing access token in case refresh token is invalid."""

        response = await test_client.post(
            "/auth/access-token/", headers={"Authorization": f"Bearer {JWT}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(side_effect=ExpiredSignatureError()))
    async def test_refresh_access_token_is_expired(
        self, test_client: AsyncClient
    ) -> None:
        """Test refreshing access token in case refresh token is expired."""

        response = await test_client.post(
            "/auth/access-token/", headers={"Authorization": f"Bearer {JWT}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.EXPIRED_TOKEN.value}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=FAKE_USER))
    async def test_refresh_access_token_user_does_not_exist(
        self, test_client: AsyncClient
    ) -> None:
        """
        Test refreshing access token in case user from refresh token does not exist.
        """

        response = await test_client.post(
            "/auth/access-token/", headers={"Authorization": f"Bearer {JWT}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED.value}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_refresh_access_token_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test refreshing access token in case user does not have appropriate scope.
        """

        response = await test_client.post(
            "/auth/access-token/", headers={"Authorization": f"Bearer {JWT}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PERMISSION_DENIED.value
        }
