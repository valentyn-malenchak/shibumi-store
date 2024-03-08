"""Module that contains tests for product routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from freezegun import freeze_time
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
    FROZEN_DATETIME,
    SHOP_SIDE_USER,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestProduct(BaseAPITest):
    """Test class for product APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_create_product(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
                "Intel Core i5-12500H (2.5 - 4.5 GHz) / RAM 16 GB / "
                "SSD 512 GB / nVidia GeForce RTX 3050, 4 GB / LAN / "
                "Wi-Fi / Bluetooth / webcamera / no OS / 2.2 kg / black",
                "description": "Very cool laptop.",
                "quantity": 12,
                "price": 1200.00,
                "category_id": "65d24f2a260fb739c605b28d",
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

        assert self._exclude_fields(response.json(), exclude_keys=["id"]) == {
            "name": "ASUS TUF Gaming F15",
            "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
            "Intel Core i5-12500H (2.5 - 4.5 GHz) / RAM 16 GB / "
            "SSD 512 GB / nVidia GeForce RTX 3050, 4 GB / LAN / "
            "Wi-Fi / Bluetooth / webcamera / no OS / 2.2 kg / black",
            "description": "Very cool laptop.",
            "quantity": 12,
            "price": 1200.00,
            "category_id": "65d24f2a260fb739c605b28d",
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

        # Check if background task calculates appropriate category parameters
        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/categories/65d24f2a260fb739c605b28d/parameters/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "65d24f2a260fb739c605b28d",
            "battery_capacity": ["56 watt*hours"],
            "brand": ["Asus"],
            "class": ["Gaming"],
            "color": ["black"],
            "country_of_production": ["Taiwan"],
            "cpu": ["Intel Core i5-12500H"],
            "cpu_cores_number": [12],
            "graphics_card": ["GeForce RTX 3050"],
            "graphics_card_type": ["Discrete"],
            "has_bluetooth": [True],
            "has_fingerprint_identification": [False],
            "has_keyboard_backlight": [False],
            "has_touch_screen": [False],
            "has_wifi": [True],
            "hdd": [None],
            "hdd_space": [None],
            "motherboard_chipset": [None],
            "no_wireless_connection": [False],
            "os": [None],
            "ram": ["16 GB"],
            "ram_slots": [2],
            "ram_type": ["DDR4"],
            "screen_refresh_rate": ["144 Hz"],
            "screen_resolution": ["1920x1080"],
            "screen_size": ['15.6"'],
            "screen_type": ["IPS"],
            "ssd": ["Kingston"],
            "ssd_space": ["512 GB"],
            "vram": ["4 GB"],
            "warranty": ["2 years"],
            "year": [2024],
        }

    @pytest.mark.asyncio
    async def test_create_product_no_token(self, test_client: AsyncClient) -> None:
        """Test create product in case there is no token."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/products/",
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
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    async def test_create_product_invalid_token(self, test_client: AsyncClient) -> None:
        """Test create product in case token is invalid."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/products/",
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
        assert response.json() == {"detail": HTTPErrorMessagesEnum.INVALID_CREDENTIALS}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_product_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case user does not have appropriate scope."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/products/",
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
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_product_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case request data is invalid."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/products/",
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
            ("missing", ["body", "price"], "Field required"),
            (
                "object_id",
                ["body", "category_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
            ),
            ("missing", ["body", "html_body"], "Field required"),
        ]

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_product_category_does_not_exist(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case request category does not exist."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": "Cool.",
                "description": "Very cool laptop.",
                "quantity": 12,
                "price": 1200.0,
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
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(  # type: ignore
                entity="Category"
            )
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_product_category_is_not_leaf(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case request category is not a tree leaf."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": "Cool.",
                "description": "Very cool laptop.",
                "quantity": 12,
                "price": 1200.0,
                "category_id": "65d24f2a260fb739c605b28a",
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
            "detail": HTTPErrorMessagesEnum.LEAF_PRODUCT_CATEGORY_REQUIRED
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_product_category_validate_product_parameters(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create product in case product parameters are invalid."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/products/",
            json={
                "name": "ASUS TUF Gaming F15",
                "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
                "Intel Core i5-12500H (2.5 - 4.5 GHz) / RAM 16 GB / "
                "SSD 512 GB / nVidia GeForce RTX 3050, 4 GB / LAN / "
                "Wi-Fi / Bluetooth / webcamera / no OS / 2.2 kg / black",
                "description": "Very cool laptop.",
                "quantity": 12,
                "price": 1200.0,
                "category_id": "65d24f2a260fb739c605b28d",
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
                ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.format(  # type: ignore
                    type_="str"
                ),
            ),
            (
                "invalid_type",
                ["body", "parameters", "ram"],
                ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.format(  # type: ignore
                    type_="str"
                ),
            ),
            (
                "invalid_type",
                ["body", "parameters", "ram_slots"],
                ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.format(  # type: ignore
                    type_="int"
                ),
            ),
            (
                "invalid_type",
                ["body", "parameters", "class"],
                ValidationErrorMessagesEnum.INVALID_FIELD_TYPE.format(  # type: ignore
                    type_="list"
                ),
            ),
            (
                "missing",
                ["body", "parameters", "has_fingerprint_identification"],
                ValidationErrorMessagesEnum.REQUIRED_FIELD,
            ),
            (
                "missing",
                ["body", "parameters", "has_keyboard_backlight"],
                ValidationErrorMessagesEnum.REQUIRED_FIELD,
            ),
            (
                "missing",
                ["body", "parameters", "has_touch_screen"],
                ValidationErrorMessagesEnum.REQUIRED_FIELD,
            ),
        ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.PRODUCTS,)],
        indirect=True,
    )
    async def test_get_product_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get product in case there is no token."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/6597f143c064f4099808ad26/"
        )

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "id": "6597f143c064f4099808ad26",
            "name": "ASUS TUF Gaming F15",
            "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
            "Intel Core i5-12500H (2.5 - 4.5 GHz) / RAM 16 GB / "
            "SSD 512 GB / nVidia GeForce RTX 3050, 4 GB / LAN / "
            "Wi-Fi / Bluetooth / webcamera / no OS / 2.2 kg / black",
            "description": "Very cool laptop.",
            "quantity": 12,
            "price": 1198.0,
            "category_id": "65d24f2a260fb739c605b28d",
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
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.PRODUCTS,)],
        indirect=True,
    )
    async def test_get_product_no_token_unavailable_product(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get product in case there is no token and product is unavailable."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/65d22fd0a83d80b9f0bd3e38/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCT_ACCESS_DENIED
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.PRODUCTS)],
        indirect=True,
    )
    async def test_get_product_authorized_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get product in case user is authorized."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/6597f143c064f4099808ad26/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "6597f143c064f4099808ad26",
            "name": "ASUS TUF Gaming F15",
            "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
            "Intel Core i5-12500H (2.5 - 4.5 GHz) / RAM 16 GB / "
            "SSD 512 GB / nVidia GeForce RTX 3050, 4 GB / LAN / "
            "Wi-Fi / Bluetooth / webcamera / no OS / 2.2 kg / black",
            "description": "Very cool laptop.",
            "quantity": 12,
            "price": 1198.0,
            "category_id": "65d24f2a260fb739c605b28d",
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
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.PRODUCTS)],
        indirect=True,
    )
    async def test_get_product_customer_user_unavailable_product(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get product in case user is authorized, but product is unavailable."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/65d22fd0a83d80b9f0bd3e38/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCT_ACCESS_DENIED
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.PRODUCTS)],
        indirect=True,
    )
    async def test_get_product_shop_side_user_unavailable_product(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test get product in case user is from shop side and product is unavailable.
        """

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/65d22fd0a83d80b9f0bd3e38/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "65d22fd0a83d80b9f0bd3e38",
            "name": "Xiaomi Mi Power Bank (BHR6109CN)",
            "synopsis": "20000 mAh 22.5W Fast Charge PB2022ZM",
            "description": "Very cool power bank.",
            "quantity": 2,
            "price": 57.69,
            "category_id": "65d24f2a260fb739c605b2a7",
            "available": False,
            "html_body": None,
            "parameters": {
                "brand": "Xiaomi",
                "year": 2023,
                "warranty": "2 years",
                "country_of_production": "China",
            },
            "created_at": "2024-02-18T16:26:56.913000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_product_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get product in case user does not have a scope."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    async def test_get_product_invalid_identifier(
        self, test_client: AsyncClient
    ) -> None:
        """Test get product in case of invalid identifier."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/invalid-group-id/"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "object_id",
                ["path", "product_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
            )
        ]

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, test_client: AsyncClient) -> None:
        """
        Test get product in case of identifier is valid, but there is no such product.
        """

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/6598495fdf97a8e0d7e612aa/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(  # type: ignore
                entity="Product"
            )
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.PRODUCTS,)], indirect=True
    )
    @patch("redis.Redis.get", lambda *args, **kwargs: None)
    @patch("redis.Redis.setex", lambda *args, **kwargs: None)
    async def test_get_products_list_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get products list in case there is no token."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={"page": 1, "page_size": 2, "available": True},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "6597f143c064f4099808ad26",
                    "name": "ASUS TUF Gaming F15",
                    "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
                    "Intel Core i5-12500H (2.5 - 4.5 GHz) / RAM 16 GB / SSD 512 GB / "
                    "nVidia GeForce RTX 3050, 4 GB / LAN / Wi-Fi / Bluetooth / "
                    "webcamera / no OS / 2.2 kg / black",
                    "quantity": 12,
                    "price": 1198.0,
                    "category_id": "65d24f2a260fb739c605b28d",
                    "available": True,
                    "created_at": "2024-01-05T12:08:35.440000",
                    "updated_at": None,
                },
                {
                    "id": "65a7f143c064f4099808ad27",
                    "name": "MSI GS66 Stealth",
                    "synopsis": "Display 15.6 IPS (1920x1080) Full HD 240 Hz / "
                    "Intel Core i9-12900H (2.5 - 5.0 GHz) / RAM 32 GB / "
                    "SSD 1 TB / nVidia GeForce RTX 3080, 8 GB / LAN / Wi-Fi "
                    "/ Bluetooth / webcam / Windows 11 Home / 2.1 kg / black",
                    "quantity": 8,
                    "price": 1600.49,
                    "category_id": "65d24f2a260fb739c605b28d",
                    "available": True,
                    "created_at": "2024-02-10T14:20:00",
                    "updated_at": None,
                },
            ],
            "total": 19,
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.PRODUCTS)],
        indirect=True,
    )
    @patch("redis.Redis.get", lambda *args, **kwargs: None)
    @patch("redis.Redis.setex", lambda *args, **kwargs: None)
    async def test_get_products_list_customer_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get products list in case user is customer."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={"page": 3, "page_size": 1, "available": True},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "65b7f143c064f4099808ad28",
                    "name": "Lenovo Legion 7i",
                    "synopsis": "Display 15.6 IPS (2560x1440) Quad HD 165 Hz / "
                    "Intel Core i7-12700H (2.5 - 4.8 GHz) / RAM 64 GB / "
                    "SSD 2 TB / NVIDIA GeForce RTX 3080 Ti, 16 GB / LAN / Wi-Fi 6 "
                    "/ Bluetooth 5.1 / webcam / Windows 11 Pro / 2.5 kg / black",
                    "quantity": 15,
                    "price": 2559.0,
                    "category_id": "65d24f2a260fb739c605b28d",
                    "available": True,
                    "created_at": "2024-03-02T09:45:00",
                    "updated_at": None,
                }
            ],
            "total": 19,
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.PRODUCTS)],
        indirect=True,
    )
    @patch("redis.Redis.get", lambda *args, **kwargs: None)
    @patch("redis.Redis.setex", lambda *args, **kwargs: None)
    async def test_get_products_list_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get products list in case user is from shop side."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={"page": 7, "page_size": 2},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "65d22fd0a83d80b9f0bd3e38",
                    "name": "Xiaomi Mi Power Bank (BHR6109CN)",
                    "synopsis": "20000 mAh 22.5W Fast Charge PB2022ZM",
                    "quantity": 2,
                    "price": 57.69,
                    "category_id": "65d24f2a260fb739c605b2a7",
                    "available": False,
                    "created_at": "2024-02-18T16:26:56.913000",
                    "updated_at": None,
                },
                {
                    "id": "65d22fd0a83d80b9f0bd3e39",
                    "name": "Anker PowerCore 26800mAh Portable Charger",
                    "synopsis": "26800mAh 3-Port USB Power Bank",
                    "quantity": 5,
                    "price": 56.2,
                    "category_id": "65d24f2a260fb739c605b2a7",
                    "available": True,
                    "created_at": "2024-02-19T09:15:00",
                    "updated_at": None,
                },
            ],
            "total": 20,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.PRODUCTS,)], indirect=True
    )
    @patch("redis.Redis.get", lambda *args, **kwargs: None)
    @patch("redis.Redis.setex", lambda *args, **kwargs: None)
    async def test_get_products_list_with_filters(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get products list with filters."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={
                "page": 1,
                "page_size": 20,
                "available": True,
                "category_id": "65d24f2a260fb739c605b28d",
                "brand": ["Asus", "Lenovo", "Dell"],
                "class": ["Gaming", "High-Performance"],
                "cpu": "Intel Core i5-12500H",
                "cpu_cores_number": 12,
                "has_bluetooth": True,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "6597f143c064f4099808ad26",
                    "name": "ASUS TUF Gaming F15",
                    "synopsis": "Display 15.6 IPS (1920x1080) Full HD 144 Hz / "
                    "Intel Core i5-12500H (2.5 - 4.5 GHz) / RAM 16 GB / SSD 512 GB "
                    "/ nVidia GeForce RTX 3050, 4 GB / LAN / Wi-Fi / Bluetooth / "
                    "webcamera / no OS / 2.2 kg / black",
                    "quantity": 12,
                    "price": 1198.0,
                    "category_id": "65d24f2a260fb739c605b28d",
                    "available": True,
                    "created_at": "2024-01-05T12:08:35.440000",
                    "updated_at": None,
                }
            ],
            "total": 1,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.PRODUCTS,)], indirect=True
    )
    @patch("redis.Redis.get", lambda *args, **kwargs: None)
    @patch("redis.Redis.setex", lambda *args, **kwargs: None)
    async def test_get_products_list_with_search(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get products list with search."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={
                "page": 1,
                "page_size": 20,
                "available": True,
                "search": "portable charger",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "65d22fd0a83d80b9f0bd3e40",
                    "name": "RAVPower Portable Charger 20000mAh",
                    "synopsis": "20000mAh Power Bank with 18W PD and QC 3.0",
                    "quantity": 10,
                    "price": 29.99,
                    "category_id": "65d24f2a260fb739c605b2a7",
                    "available": True,
                    "created_at": "2024-02-20T11:30:00",
                    "updated_at": None,
                },
                {
                    "id": "65d22fd0a83d80b9f0bd3e41",
                    "name": "Samsung Wireless Charger Portable Battery",
                    "synopsis": "10000mAh Wireless Power Bank with USB-C, Silver",
                    "quantity": 8,
                    "price": 170.58,
                    "category_id": "65d24f2a260fb739c605b2a7",
                    "available": True,
                    "created_at": "2024-02-21T14:20:00",
                    "updated_at": None,
                },
                {
                    "id": "65d22fd0a83d80b9f0bd3e39",
                    "name": "Anker PowerCore 26800mAh Portable Charger",
                    "synopsis": "26800mAh 3-Port USB Power Bank",
                    "quantity": 5,
                    "price": 56.2,
                    "category_id": "65d24f2a260fb739c605b2a7",
                    "available": True,
                    "created_at": "2024-02-19T09:15:00",
                    "updated_at": None,
                },
            ],
            "total": 3,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.PRODUCTS,)], indirect=True
    )
    @patch("redis.Redis.get", lambda *args, **kwargs: None)
    @patch("redis.Redis.setex", lambda *args, **kwargs: None)
    async def test_get_products_list_with_sorting(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get products list with sorting."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={
                "page": 1,
                "page_size": 2,
                "available": True,
                "category_id": "65d24f2a260fb739c605b28d",
                "sort_by": "parameters.cpu_cores_number",
                "sort_order": "asc",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "65d7f143c064f4099808ad30",
                    "name": "HP Envy x360",
                    "synopsis": "Display 13.3 IPS (1920x1080) Full HD Touchscreen / "
                    "AMD Ryzen 7 5700U (1.8 - 4.3 GHz) / RAM 8 GB / SSD 256 GB / "
                    "AMD Radeon Graphics / Wi-Fi 6 / Bluetooth 5.2 / webcam / "
                    "Windows 11 Home / 1.3 kg / silver",
                    "quantity": 18,
                    "price": 599.99,
                    "category_id": "65d24f2a260fb739c605b28d",
                    "available": True,
                    "created_at": "2024-04-05T10:15:00",
                    "updated_at": None,
                },
                {
                    "id": "65c7f143c064f4099808ad29",
                    "name": "Acer Predator Helios 300",
                    "synopsis": "Display 17.3 IPS (1920x1080) Full HD 144 Hz / "
                    "Intel Core i7-11800H (2.3 - 4.6 GHz) / RAM 32 GB / "
                    "SSD 1 TB / NVIDIA GeForce RTX 3070, 8 GB / LAN / Wi-Fi 6 / "
                    "Bluetooth 5.0 / webcam / Windows 10 Home / 3.1 kg / black",
                    "quantity": 20,
                    "price": 1066.0,
                    "category_id": "65d24f2a260fb739c605b28d",
                    "available": True,
                    "created_at": "2024-03-15T14:30:00",
                    "updated_at": None,
                },
            ],
            "total": 12,
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_products_list_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get products list in case user does not have a scope."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    async def test_get_products_list_validate_base_filters(
        self, test_client: AsyncClient
    ) -> None:
        """Test get products list in case base query parameters are invalid."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={
                "available": "maybe",
                "sort_by": "random_field",
                "sort_order": "any",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "bool_parsing",
                ["query", "available"],
                "Input should be a valid boolean, unable to interpret input",
            ),
            ("enum", ["query", "sort_order"], "Input should be 'asc' or 'desc'"),
            ("missing", ["query", "page"], "Field required"),
            ("missing", ["query", "page_size"], "Field required"),
        ]

    @pytest.mark.asyncio
    @patch(
        "redis.Redis.get",
        lambda *args, **kwargs: '[{"machine_name":"cpu_cores_number"'
        ',"type":"INT"},{"machine_name":"has_wifi","type":"BOOL"}]',
    )
    async def test_get_products_list_validate_product_parameters_filters(
        self, test_client: AsyncClient
    ) -> None:
        """Test get products list in case product parameters filter are invalid."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={
                "page": 1,
                "page_size": 2,
                "available": True,
                "has_wifi": "sure",
                "cpu_cores_number": "two",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "int_parsing",
                ["cpu_cores_number", 0],
                "Input should be a valid integer, unable to parse string as an integer",
            ),
            (
                "bool_parsing",
                ["has_wifi", 0],
                "Input should be a valid boolean, unable to interpret input",
            ),
        ]

    @pytest.mark.asyncio
    async def test_get_products_list_no_token_not_available_products(
        self, test_client: AsyncClient
    ) -> None:
        """
        Test get products list in case there is no token and user requests
        not available products.
        """

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={"page": 1, "page_size": 2},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCTS_NOT_AVAILABLE_ACCESS_DENIED
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_products_list_customer_user_not_available_products(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test get products list in case user is customer and requests not available
        products.
        """

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/products/",
            params={"page": 3, "page_size": 1, "available": False},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCTS_NOT_AVAILABLE_ACCESS_DENIED
        }
