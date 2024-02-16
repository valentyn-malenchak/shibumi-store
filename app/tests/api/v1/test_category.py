"""Module that contains tests for category routes."""


from unittest.mock import Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.constants import HTTPErrorMessagesEnum, ValidationErrorMessagesEnum
from app.services.mongo.constants import MongoCollectionsEnum
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    CUSTOMER_USER,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestCategory(BaseAPITest):
    """Test class for category APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    async def test_get_categories_list_no_token(self, test_client: AsyncClient) -> None:
        """Test get categories list in case there is no token."""

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
                    "created_at",
                    "updated_at",
                }
                == set(dictionary.keys())
                for dictionary in response.json()["data"]
            )
            is True
        )
        assert response.json()["total"] == 31  # noqa: PLR2004

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
                    "created_at",
                    "updated_at",
                }
                == set(dictionary.keys())
                for dictionary in response.json()["data"]
            )
            is True
        )
        assert response.json()["total"] == 31  # noqa: PLR2004

    @pytest.mark.asyncio
    async def test_get_categories_list_with_filters(
        self, test_client: AsyncClient
    ) -> None:
        """Test get categories list with filters."""

        response = await test_client.get(
            "/categories/",
            params={"path": "/electronics/computers", "leafs": True},
        )

        assert response.status_code == status.HTTP_200_OK
        assert self._exclude_fields(
            response.json(),
            exclude_keys=["id", "parent_id", "created_at", "updated_at"],
        ) == {
            "data": [
                {
                    "name": "Desktop Computers",
                    "description": "Desktop PCs",
                    "path": "/electronics/computers/desktops",
                    "path_name": "desktops",
                },
                {
                    "name": "Laptop Computers",
                    "description": "Laptop PCs",
                    "path": "/electronics/computers/laptops",
                    "path_name": "laptops",
                },
                {
                    "name": "All-in-One Computers",
                    "description": "All-in-One PCs",
                    "path": "/electronics/computers/all-in-one",
                    "path_name": "all-in-one",
                },
            ],
            "total": 3,
        }

    @pytest.mark.asyncio
    async def test_get_category_no_token(self, test_client: AsyncClient) -> None:
        """Test get category in case there is no token."""

        categories = await test_client.get("/categories/")

        category_id = next(
            category["id"]
            for category in categories.json()["data"]
            if category["path"] == "/electronics"
        )

        response = await test_client.get(f"/categories/{category_id}/")

        assert response.status_code == status.HTTP_200_OK

        assert self._exclude_fields(
            response.json(),
            exclude_keys=["id", "created_at", "updated_at"],
        ) == {
            "name": "Electronics",
            "description": "Electronic devices",
            "parent_id": None,
            "path": "/electronics",
            "path_name": "electronics",
            "parameters": [],
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_get_category_authorized_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get category in case user is authorized."""

        categories = await test_client.get("/categories/")

        category_id = next(
            category["id"]
            for category in categories.json()["data"]
            if category["path"]
            == "/electronics/accessories/mobile-accessories/power-banks"
        )

        response = await test_client.get(
            f"/categories/{category_id}/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert self._exclude_fields(
            response.json(),
            exclude_keys=["id", "parent_id", "created_at", "updated_at"],
        ) == {
            "name": "Power Banks",
            "description": "Power banks for mobile devices",
            "path": "/electronics/accessories/mobile-accessories/power-banks",
            "path_name": "power-banks",
            "parameters": [
                {
                    "name": "Brand",
                    "machine_name": "brand",
                    "type": "STR",
                },
                {
                    "name": "Manufacture year",
                    "machine_name": "year",
                    "type": "INT",
                },
                {
                    "name": "Warranty",
                    "machine_name": "warranty",
                    "type": "STR",
                },
                {
                    "name": "County of production",
                    "machine_name": "country_of_production",
                    "type": "STR",
                },
            ],
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_get_category_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get category in case user does not have a scope."""

        response = await test_client.get(
            "/categories/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PERMISSION_DENIED.value
        }

    @pytest.mark.asyncio
    async def test_get_category_invalid_identifier(
        self, test_client: AsyncClient
    ) -> None:
        """Test get category in case of invalid identifier."""

        response = await test_client.get("/categories/invalid-group-id/")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "object_id",
                ["path", "category_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER.value,
            )
        ]

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, test_client: AsyncClient) -> None:
        """
        Test get category in case of identifier is valid, but there is no such category.
        """

        response = await test_client.get("/categories/6598495fdf97a8e0d7e612aa/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.value.format(
                entity="Category"
            )
        }
