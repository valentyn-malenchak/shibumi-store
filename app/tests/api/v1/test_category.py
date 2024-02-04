"""Module that contains tests for category routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.services.mongo.constants import MongoCollectionsEnum
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    CUSTOMER_USER,
    TEST_JWT,
)


class TestCategory(BaseAPITest):
    """Test class for category APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    async def test_get_categories_list_unauthorized_user(
        self, test_client: AsyncClient
    ) -> None:
        """Test get categories list in case user is unauthorized."""

        response = await test_client.get("/categories/")

        assert response.status_code == status.HTTP_200_OK
        assert (
            all(
                {
                    "id",
                    "name",
                    "description",
                    "parent_id",
                    "path",
                    "path_name",
                }.issubset(dictionary.keys())
                for dictionary in response.json()["data"]
            )
            is True
        )
        assert all(item in response.json().items() for item in dict(total=31).items())

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_get_categories_list_authorized_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get categories list in case user is authorized."""

        response = await test_client.get(
            "/categories/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert (
            all(
                {
                    "id",
                    "name",
                    "description",
                    "parent_id",
                    "path",
                    "path_name",
                }.issubset(dictionary.keys())
                for dictionary in response.json()["data"]
            )
            is True
        )
        assert all(item in response.json().items() for item in dict(total=31).items())

    @pytest.mark.asyncio
    async def test_get_categories_list_with_filters(
        self, test_client: AsyncClient
    ) -> None:
        """Test get categories list with filters."""

        response = await test_client.get(
            "/categories/",
            params={"path": "/electronics/computers/"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert {category["path"] for category in response.json()["data"]} == {
            "/electronics/computers/desktops",
            "/electronics/computers/laptops",
            "/electronics/computers/all-in-one",
        }
        assert all(item in response.json().items() for item in dict(total=3).items())
