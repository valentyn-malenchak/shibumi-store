"""Module that contains tests for users routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from jose import ExpiredSignatureError

from app.constants import HTTPErrorMessages
from app.tests.api_v1 import BaseTest
from app.tests.constants import FAKE_USER, JWT, USER


class TestUser(BaseTest):
    """Test class for users API endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER))
    async def test_get_me(self, test_client: AsyncClient, arrange_db: None) -> None:
        """Test get me."""

        response = await test_client.get(
            "/users/me/",
            headers={"Authorization": f"Bearer {JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "65844f12b6de26578d98c2c8",
            "first_name": "John",
            "last_name": "Smith",
            "patronymic_name": None,
            "username": "john.smith",
            "email": "john.smith@gmail.com",
            "phone_number": "+380981111111",
            "birthdate": "1998-01-01",
        }

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, test_client: AsyncClient) -> None:
        """Test get me in case there is no token."""

        response = await test_client.get("/users/me/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, test_client: AsyncClient) -> None:
        """Test get me in case refresh token is invalid."""

        response = await test_client.get(
            "/users/me/",
            headers={"Authorization": f"Bearer {JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessages.INVALID_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(side_effect=ExpiredSignatureError()))
    async def test_get_me_access_token_is_expired(
        self, test_client: AsyncClient
    ) -> None:
        """Test get me in case refresh token is expired."""

        response = await test_client.get(
            "/users/me/", headers={"Authorization": f"Bearer {JWT}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessages.EXPIRED_TOKEN.value}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=FAKE_USER))
    async def test_get_me_user_does_not_exist(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test get me in case user from refresh token does not exist.
        """

        response = await test_client.get(
            "/users/me/", headers={"Authorization": f"Bearer {JWT}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessages.ENTITY_IS_NOT_FOUND.value.format(entity="User")
        }
