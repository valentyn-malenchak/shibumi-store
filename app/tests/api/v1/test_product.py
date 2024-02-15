"""Module that contains tests for product routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from freezegun import freeze_time
from httpx import AsyncClient

from app.constants import HTTPErrorMessagesEnum, ValidationErrorMessagesEnum
from app.services.mongo.constants import MongoCollectionsEnum
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    FROZEN_DATETIME,
    SHOP_SIDE_USER,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestProduct(BaseAPITest):
    """Test class for product APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    @freeze_time(FROZEN_DATETIME)
    async def test_create_product(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product."""

        categories = await test_client.get(
            "/categories/", headers={"Authorization": f"Bearer {TEST_JWT}"}
        )

        category_id = next(
            category["id"]
            for category in categories.json()["data"]
            if category["path"] == "/electronics/computers/laptops"
        )

        response = await test_client.post(
            "/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
                "Intel Core i5-12500H (2.5 - 4.5 ГГц) / RAM 16 ГБ / "
                "SSD 512 ГБ / nVidia GeForce RTX 3050, 4 ГБ / LAN / "
                "Wi-Fi / Bluetooth / webcamera / no OS / 2.2 кг / black",
                "description": "Very cool laptop.",
                "quantity": 12,
                "category_id": category_id,
                "available": True,
                "html_body": None,
                "parameters": {
                    "brand": "Asus",
                    "cpu": "Intel Core i5-12500H",
                    "cpu_cores_number": 12,
                    "graphics_card": "GeForce RTX 3050",
                    "graphics_card_type": "Discrete",
                    "motherboard_chipset": None,
                    "vram": "4 GB",
                    "ram": "16 GB",
                    "ram_slots": 2,
                    "ram_type": "DDR4",
                    "hdd": None,
                    "hdd_space": None,
                    "ssd": "Kingston",
                    "ssd_space": "512 GB",
                    "class": ["Gaming"],
                    "has_wifi": True,
                    "has_bluetooth": True,
                    "no_wireless_connection": False,
                    "os": None,
                    "year": 2024,
                    "warranty": "2 years",
                    "country_of_production": "Taiwan",
                    "screen_type": "IPS",
                    "screen_resolution": "1920x1080",
                    "screen_refresh_rate": "144 Hz",
                    "screen_size": '15.6"',
                    "battery_capacity": "56 watt*hours",
                    "has_fingerprint_identification": False,
                    "has_keyboard_backlight": False,
                    "has_touch_screen": False,
                    "color": "black",
                    "custom_field": "some_value",
                },
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert {
            key: value for key, value in response.json().items() if key != "id"
        } == {
            "name": "ASUS TUF Gaming F15",
            "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
            "Intel Core i5-12500H (2.5 - 4.5 ГГц) / RAM 16 ГБ / "
            "SSD 512 ГБ / nVidia GeForce RTX 3050, 4 ГБ / LAN / "
            "Wi-Fi / Bluetooth / webcamera / no OS / 2.2 кг / black",
            "description": "Very cool laptop.",
            "quantity": 12,
            "category_id": category_id,
            "available": True,
            "html_body": None,
            "parameters": {
                "brand": "Asus",
                "cpu": "Intel Core i5-12500H",
                "cpu_cores_number": 12,
                "graphics_card": "GeForce RTX 3050",
                "graphics_card_type": "Discrete",
                "motherboard_chipset": None,
                "vram": "4 GB",
                "ram": "16 GB",
                "ram_slots": 2,
                "ram_type": "DDR4",
                "hdd": None,
                "hdd_space": None,
                "ssd": "Kingston",
                "ssd_space": "512 GB",
                "class": ["Gaming"],
                "has_wifi": True,
                "has_bluetooth": True,
                "no_wireless_connection": False,
                "os": None,
                "year": 2024,
                "warranty": "2 years",
                "country_of_production": "Taiwan",
                "screen_type": "IPS",
                "screen_resolution": "1920x1080",
                "screen_refresh_rate": "144 Hz",
                "screen_size": '15.6"',
                "battery_capacity": "56 watt*hours",
                "has_fingerprint_identification": False,
                "has_keyboard_backlight": False,
                "has_touch_screen": False,
                "color": "black",
                "custom_field": "some_value",
            },
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_product_no_token(self, test_client: AsyncClient) -> None:
        """Test create product in case there is no token."""

        response = await test_client.post(
            "/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": None,
                "description": "Very cool laptop.",
                "quantity": 12,
                "category_id": "65cd1a06f2fa373a2e2a7ea4",
                "available": True,
                "html_body": None,
                "parameters": {
                    "brand": "Asus",
                },
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED.value}

    @pytest.mark.asyncio
    async def test_create_product_invalid_token(self, test_client: AsyncClient) -> None:
        """Test create product in case token is invalid."""

        response = await test_client.post(
            "/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": None,
                "description": "Very cool laptop.",
                "quantity": 12,
                "category_id": "65cd1a06f2fa373a2e2a7ea4",
                "available": True,
                "html_body": None,
                "parameters": {
                    "brand": "Asus",
                },
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_product_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case user does not have appropriate scope."""

        response = await test_client.post(
            "/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": None,
                "description": "Very cool laptop.",
                "quantity": 12,
                "category_id": "65cd1a06f2fa373a2e2a7ea4",
                "available": True,
                "html_body": None,
                "parameters": {
                    "brand": "Asus",
                },
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PERMISSION_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_product_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case request data is invalid."""

        response = await test_client.post(
            "/products/",
            json={
                "synopsis": None,
                "description": "Very cool laptop.",
                "quantity": 12,
                "category_id": 1,
                "available": True,
                "parameters": {
                    "brand": "Asus",
                },
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "name"], "Field required"),
            ("string_type", ["body", "synopsis"], "Input should be a valid string"),
            (
                "object_id",
                ["body", "category_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER.value,
            ),
            ("missing", ["body", "html_body"], "Field required"),
        ]

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_product_category_does_not_exist(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case request category does not exist."""

        response = await test_client.post(
            "/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": "Cool.",
                "description": "Very cool laptop.",
                "quantity": 12,
                "category_id": "62cd1a06f2fa373a2e2a7ea1",
                "available": True,
                "html_body": None,
                "parameters": {
                    "brand": "Asus",
                },
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.value.format(
                entity="Category"
            )
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_product_category_is_not_leaf(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case request category is not a tree leaf."""

        categories = await test_client.get(
            "/categories/", headers={"Authorization": f"Bearer {TEST_JWT}"}
        )

        category_id = next(
            category["id"]
            for category in categories.json()["data"]
            if category["path"] == "/electronics"
        )

        response = await test_client.post(
            "/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": "Cool.",
                "description": "Very cool laptop.",
                "quantity": 12,
                "category_id": category_id,
                "available": True,
                "html_body": None,
                "parameters": {
                    "brand": "Asus",
                },
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.LEAF_PRODUCT_CATEGORY_REQUIRED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_product_category_validate_product_parameters(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case product parameters are invalid."""

        categories = await test_client.get(
            "/categories/", headers={"Authorization": f"Bearer {TEST_JWT}"}
        )

        category_id = next(
            category["id"]
            for category in categories.json()["data"]
            if category["path"] == "/electronics/computers/laptops"
        )

        response = await test_client.post(
            "/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
                "Intel Core i5-12500H (2.5 - 4.5 ГГц) / RAM 16 ГБ / "
                "SSD 512 ГБ / nVidia GeForce RTX 3050, 4 ГБ / LAN / "
                "Wi-Fi / Bluetooth / webcamera / no OS / 2.2 кг / black",
                "description": "Very cool laptop.",
                "quantity": 12,
                "category_id": category_id,
                "available": True,
                "html_body": None,
                "parameters": {
                    "brand": "Asus",
                    "cpu": "Intel Core i5-12500H",
                    "cpu_cores_number": 12,
                    "graphics_card": "GeForce RTX 3050",
                    "graphics_card_type": "Discrete",
                    "motherboard_chipset": None,
                    "vram": 4,
                    "ram": 16,
                    "ram_slots": "2",
                    "ram_type": "DDR4",
                    "hdd": None,
                    "hdd_space": None,
                    "ssd": "Kingston",
                    "ssd_space": "512 GB",
                    "class": "Gaming",
                    "has_wifi": True,
                    "has_bluetooth": True,
                    "no_wireless_connection": False,
                    "os": None,
                    "year": 2024,
                    "warranty": "2 years",
                    "country_of_production": "Taiwan",
                    "screen_type": "IPS",
                    "screen_resolution": "1920x1080",
                    "screen_refresh_rate": "144 Hz",
                    "screen_size": '15.6"',
                    "battery_capacity": "56 watt*hours",
                    "color": "black",
                    "custom_field": "some_value",
                },
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "invalid_type",
                ["body", "parameters", "vram"],
                ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.value.format(
                    type_="str"
                ),
            ),
            (
                "invalid_type",
                ["body", "parameters", "ram"],
                ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.value.format(
                    type_="str"
                ),
            ),
            (
                "invalid_type",
                ["body", "parameters", "ram_slots"],
                ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.value.format(
                    type_="int"
                ),
            ),
            (
                "invalid_type",
                ["body", "parameters", "class"],
                ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.value.format(
                    type_="list"
                ),
            ),
            (
                "missing",
                ["body", "parameters", "has_fingerprint_identification"],
                ValidationErrorMessagesEnum.REQUIRED_FIELD.value,
            ),
            (
                "missing",
                ["body", "parameters", "has_keyboard_backlight"],
                ValidationErrorMessagesEnum.REQUIRED_FIELD.value,
            ),
            (
                "missing",
                ["body", "parameters", "has_touch_screen"],
                ValidationErrorMessagesEnum.REQUIRED_FIELD.value,
            ),
        ]