"""Module that contains tests for auth routes."""


from unittest.mock import Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from jose import ExpiredSignatureError

from app.constants import HTTPErrorMessages
from app.tests.api_v1 import BaseTest
from app.tests.constants import FAKE_USER, JWT, USER


class TestAuth(BaseTest):
    """Test class for auth API endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    async def test_create_tokens(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test auth token creation."""

        response = await test_client.post(
            "/auth/tokens/",
            data={"username": "john.smith", "password": "john1234"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_200_OK
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
        assert response.json() == {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "password"],
                    "msg": "Field required",
                    "input": None,
                    "url": "https://errors.pydantic.dev/2.5/v/missing",
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_create_tokens_user_does_not_exist(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test auth token creation in case user with such username does not exist."""

        response = await test_client.post(
            "/auth/tokens/",
            data={"username": "joe.smith", "password": "john1234"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": HTTPErrorMessages.INCORRECT_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    async def test_create_tokens_invalid_password(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test auth token creation in case user with such username does not exist."""

        response = await test_client.post(
            "/auth/tokens/",
            data={"username": "john.smith", "password": "john1234smith"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": HTTPErrorMessages.INCORRECT_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER))
    async def test_refresh_access_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test refreshing access token."""

        response = await test_client.post(
            "/auth/access-token/",
            json={"refresh_token": JWT},
        )

        assert response.status_code == status.HTTP_200_OK
        assert set(response.json().keys()) == {"access_token", "token_type"}

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_token(
        self, test_client: AsyncClient
    ) -> None:
        """Test refreshing access token in case refresh token is invalid."""

        response = await test_client.post(
            "/auth/access-token/",
            json={"refresh_token": JWT},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessages.INVALID_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(side_effect=ExpiredSignatureError()))
    async def test_refresh_access_token_is_expired(
        self, test_client: AsyncClient
    ) -> None:
        """Test refreshing access token in case refresh token is expired."""

        response = await test_client.post(
            "/auth/access-token/", json={"refresh_token": JWT}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessages.EXPIRED_TOKEN.value}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=FAKE_USER))
    async def test_refresh_access_token_user_does_not_exist(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test refreshing access token in case user from refresh token does not exist.
        """

        response = await test_client.post(
            "/auth/access-token/", json={"refresh_token": JWT}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessages.ENTITY_IS_NOT_FOUND.value.format(entity="User")
        }
