"""Module that contains tests for category routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.constants import (
    AppConstants,
    HTTPErrorMessagesEnum,
    ValidationErrorMessagesEnum,
)
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

        response = await test_client.get(f"{AppConstants.API_V1_PREFIX}/categories/")

        assert response.status_code == status.HTTP_200_OK
        assert (
            all(
                {
                    "id",
                    "name",
                    "description",
                    "parent_id",
                    "path",
                    "machine_name",
                    "created_at",
                    "updated_at",
                }
                == dictionary.keys()
                for dictionary in response.json()["data"]
            )
            is True
        )
        assert response.json()["total"] == 31  # noqa: PLR2004

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_categories_list_authorized_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get categories list in case user is authorized."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/",
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
                    "machine_name",
                    "created_at",
                    "updated_at",
                }
                == dictionary.keys()
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
            f"{AppConstants.API_V1_PREFIX}/categories/",
            params={"path": "/electronics/computers", "leafs": True},
        )

        assert response.status_code == status.HTTP_200_OK
        assert self._exclude_fields(
            response.json(),
            exclude_keys=["created_at", "updated_at"],
        ) == {
            "data": [
                {
                    "id": "65d24f2a260fb739c605b28c",
                    "name": "Desktop Computers",
                    "description": "Desktop PCs",
                    "parent_id": "65d24f2a260fb739c605b28b",
                    "path": "/electronics/computers/desktops",
                    "machine_name": "desktops",
                },
                {
                    "id": "65d24f2a260fb739c605b28d",
                    "name": "Laptop Computers",
                    "description": "Laptop PCs",
                    "parent_id": "65d24f2a260fb739c605b28b",
                    "path": "/electronics/computers/laptops",
                    "machine_name": "laptops",
                },
                {
                    "id": "65d24f2a260fb739c605b28e",
                    "name": "All-in-One Computers",
                    "description": "All-in-One PCs",
                    "parent_id": "65d24f2a260fb739c605b28b",
                    "path": "/electronics/computers/all-in-one",
                    "machine_name": "all-in-one",
                },
            ],
            "total": 3,
        }

    @pytest.mark.asyncio
    async def test_get_category_no_token(self, test_client: AsyncClient) -> None:
        """Test get category in case there is no token."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/65d24f2a260fb739c605b28a/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert self._exclude_fields(
            response.json(),
            exclude_keys=["created_at", "updated_at"],
        ) == {
            "id": "65d24f2a260fb739c605b28a",
            "name": "Electronics",
            "description": "Electronic devices",
            "parent_id": None,
            "path": "/electronics",
            "machine_name": "electronics",
            "parameters": [],
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_category_authorized_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get category in case user is authorized."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/65d24f2a260fb739c605b2a7/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert self._exclude_fields(
            response.json(),
            exclude_keys=["id", "created_at", "updated_at"],
        ) == {
            "name": "Power Banks",
            "description": "Power banks for mobile devices",
            "parent_id": "65d24f2a260fb739c605b2a3",
            "path": "/electronics/accessories/mobile-accessories/power-banks",
            "machine_name": "power-banks",
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
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_category_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get category in case user does not have a scope."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    async def test_get_category_invalid_identifier(
        self, test_client: AsyncClient
    ) -> None:
        """Test get category in case of invalid identifier."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/invalid-group-id/"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "object_id",
                ["path", "category_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
            )
        ]

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, test_client: AsyncClient) -> None:
        """
        Test get category in case of identifier is valid, but there is no such category.
        """

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/6598495fdf97a8e0d7e612aa/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(
                entity="Category"
            )
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.CATEGORY_PARAMETERS,)], indirect=True
    )
    async def test_get_category_parameters_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get category parameters in case there is no token."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/65d24f2a260fb739c605b28d/parameters/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "65d24f2a260fb739c605b28d",
            "battery_capacity": [
                "43 watt*hours",
                "45 watt*hours",
                "49.9 watt*hours",
                "56 watt*hours",
                "58 watt*hours",
                "68 watt*hours",
                "70 watt*hours",
                "80 watt*hours",
                "86 watt*hours",
                "99.9 watt*hours",
            ],
            "brand": [
                "Acer",
                "Alienware",
                "Apple",
                "Asus",
                "Dell",
                "HP",
                "Huawei",
                "Lenovo",
                "Microsoft",
                "MSI",
                "Razer",
                "Samsung",
            ],
            "class": [
                "Affordable",
                "Convertible",
                "Gaming",
                "High-Performance",
                "Multimedia",
                "Premium",
                "Ultrabook",
            ],
            "color": [
                "black",
                "emerald green",
                "lunar light",
                "mystic bronze",
                "platinum",
                "silver",
            ],
            "country_of_production": ["China", "South Korea", "Taiwan"],
            "cpu": [
                "AMD Ryzen 7 5700U",
                "Apple M2 Chip",
                "Intel Core i5-12400H",
                "Intel Core i5-12500H",
                "Intel Core i7-11800H",
                "Intel Core i7-1260U",
                "Intel Core i7-12700H",
                "Intel Core i7-12700U",
                "Intel Core i7-1270U",
                "Intel Core i9-12900H",
                "Intel Core i9-12900HK",
            ],
            "cpu_cores_number": [8, 12, 14],
            "graphics_card": [
                "AMD Radeon Graphics",
                "Apple Integrated GPU",
                "GeForce RTX 3050",
                "GeForce RTX 3050 Ti",
                "GeForce RTX 3070",
                "GeForce RTX 3080",
                "GeForce RTX 3080 Ti",
                "GeForce RTX 3090",
                "Intel Iris Xe Graphics",
                "Intel UHD Graphics",
                "NVIDIA GeForce MX450",
            ],
            "graphics_card_type": ["Discrete", "Integrated"],
            "has_bluetooth": [True],
            "has_fingerprint_identification": [False, True],
            "has_keyboard_backlight": [False, True],
            "has_touch_screen": [False, True],
            "has_wifi": [True],
            "hdd": [None],
            "hdd_space": [None],
            "motherboard_chipset": [None],
            "no_wireless_connection": [False],
            "os": [
                "macOS Monterey",
                "Windows 10 Home",
                "Windows 11 Home",
                "Windows 11 Pro",
                None,
            ],
            "ram": ["12 GB", "16 GB", "32 GB", "64 GB", "8 GB"],
            "ram_slots": [2, 4],
            "ram_type": ["DDR4", "DDR5", "LPDDR4X", "LPDDR5"],
            "screen_refresh_rate": ["120 Hz", "144 Hz", "165 Hz", "240 Hz", "60 Hz"],
            "screen_resolution": [
                "1920x1080",
                "2400x1600",
                "2560x1440",
                "2560x1600",
                "3000x2000",
                "3840x2160",
            ],
            "screen_size": ['13.3"', '14"', '14.4"', '15.6"', '17.3"'],
            "screen_type": ["IPS", "OLED", "Super AMOLED"],
            "ssd": ["Apple", "Kingston", "Samsung", "Toshiba", "Western Digital"],
            "ssd_space": ["1 TB", "2 TB", "256 GB", "512 GB"],
            "vram": ["16 GB", "2 GB", "4 GB", "8 GB", "Shared"],
            "warranty": ["1 year", "2 years", "3 years"],
            "year": [2024],
        }

    @pytest.mark.asyncio
    async def test_get_category_parameters_no_calculated_parameters(
        self, test_client: AsyncClient
    ) -> None:
        """
        Test get category parameters in case there is no calculated parameters for
        category.
        """

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/65d24f2a260fb739c605b28d/parameters/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.CATEGORY_PARAMETERS)],
        indirect=True,
    )
    async def test_get_category_parameters_authorized_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get category parameters in case is authorized."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/65d24f2a260fb739c605b2a7/parameters/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "65d24f2a260fb739c605b2a7",
            "brand": ["Anker", "RAVPower", "Samsung", "Xiaomi"],
            "country_of_production": ["China", "South Korea"],
            "warranty": ["1 year", "18 months", "2 years"],
            "year": [2023, 2024],
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_category_parameters_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get category parameters in case user does not have a scope."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/65d24f2a260fb739c605b2a7/parameters/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    async def test_get_category_parameters_invalid_identifier(
        self, test_client: AsyncClient
    ) -> None:
        """Test get category parameters in case of invalid identifier."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/invalid-group-id/parameters/"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "object_id",
                ["path", "category_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
            )
        ]

    @pytest.mark.asyncio
    async def test_get_category_parameters_not_found(
        self, test_client: AsyncClient
    ) -> None:
        """
        Test get category parameters in case of identifier is valid, but there is no
        such category.
        """

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/6598495fdf97a8e0d7e612aa/parameters/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(
                entity="Category"
            )
        }
