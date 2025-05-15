"""Module that contains tests for role routes."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.services.mongo.constants import MongoCollectionsEnum
from app.settings import SETTINGS
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    CUSTOMER_USER,
    TEST_JWT,
)


class TestRole(BaseAPITest):
    """Test class for role APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    async def test_get_roles_list_no_token(
        self,
        test_client: AsyncClient,
        redis_get_mock: AsyncMock,
        redis_setex_mock: AsyncMock,
    ) -> None:
        """Test get roles list in case there is no token."""

        response = await test_client.get(f"{SETTINGS.APP_API_V1_PREFIX}/roles/")

        assert redis_get_mock.call_count == 2  # noqa: PLR2004
        assert redis_setex_mock.call_count == 1

        assert response.status_code == status.HTTP_200_OK
        assert self._exclude_fields(
            response.json(), exclude_keys=["id", "created_at"]
        ) == {
            "data": [
                {
                    "name": "Customer",
                    "machine_name": "customer",
                    "updated_at": None,
                },
                {
                    "name": "Support",
                    "machine_name": "support",
                    "updated_at": None,
                },
                {
                    "name": "Warehouse Stuff",
                    "machine_name": "warehouse_stuff",
                    "updated_at": None,
                },
                {
                    "name": "Content Manager",
                    "machine_name": "content_manager",
                    "updated_at": None,
                },
                {
                    "name": "Marketing Manager",
                    "machine_name": "marketing_manager",
                    "updated_at": None,
                },
                {
                    "name": "Admin",
                    "machine_name": "admin",
                    "updated_at": None,
                },
            ],
            "total": 6,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("db", [(MongoCollectionsEnum.USERS,)], indirect=True)
    async def test_get_roles_list_authorized_user(
        self,
        test_client: AsyncClient,
        db: None,
        redis_get_mock: AsyncMock,
        redis_setex_mock: AsyncMock,
    ) -> None:
        """Test get roles list in case user is authorized."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/roles/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert redis_get_mock.call_count == 2  # noqa: PLR2004
        assert redis_setex_mock.call_count == 1

        assert response.status_code == status.HTTP_200_OK
        assert self._exclude_fields(
            response.json(), exclude_keys=["id", "created_at"]
        ) == {
            "data": [
                {
                    "name": "Customer",
                    "machine_name": "customer",
                    "updated_at": None,
                },
                {
                    "name": "Support",
                    "machine_name": "support",
                    "updated_at": None,
                },
                {
                    "name": "Warehouse Stuff",
                    "machine_name": "warehouse_stuff",
                    "updated_at": None,
                },
                {
                    "name": "Content Manager",
                    "machine_name": "content_manager",
                    "updated_at": None,
                },
                {
                    "name": "Marketing Manager",
                    "machine_name": "marketing_manager",
                    "updated_at": None,
                },
                {
                    "name": "Admin",
                    "machine_name": "admin",
                    "updated_at": None,
                },
            ],
            "total": 6,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "redis_get_mock",
        [
            '[{"_id": {"$oid": "65f0a17b39d1c27e2e6933e5"}, "name": "Customer", '
            '"machine_name": "customer", "created_at": {"$date": '
            '"2024-03-12T18:39:55.955Z"}, "updated_at": null}]'
        ],
        indirect=True,
    )
    async def test_get_roles_from_redis_cache(
        self,
        test_client: AsyncClient,
        redis_get_mock: AsyncMock,
    ) -> None:
        """Test get roles list in roles are cached by Redis."""

        response = await test_client.get(f"{SETTINGS.APP_API_V1_PREFIX}/roles/")

        assert redis_get_mock.call_count == 2  # noqa: PLR2004

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "65f0a17b39d1c27e2e6933e5",
                    "name": "Customer",
                    "machine_name": "customer",
                    "created_at": "2024-03-12T18:39:55.955000",
                    "updated_at": None,
                },
            ],
            "total": 1,
        }
