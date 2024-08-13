"""Module that contains tests for cart routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from freezegun import freeze_time
from httpx import AsyncClient

from app.constants import (
    AppConstants,
    HTTPErrorMessagesEnum,
)
from app.services.mongo.constants import MongoCollectionsEnum
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    CUSTOMER_USER,
    FROZEN_DATETIME,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestCart(BaseAPITest):
    """Test class for cart APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
            )
        ],
        indirect=True,
    )
    async def test_get_cart(self, test_client: AsyncClient, arrange_db: None) -> None:
        """Test get cart."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/carts/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "id": "663ce924336962a87b140742",
            "user_id": "65844f12b6de26578d98c2c8",
            "products": [
                {
                    "id": "65d22fd0a83d80b9f0bd3e39",
                    "quantity": 2,
                },
                {"id": "65d22fd0a83d80b9f0bd3e42", "quantity": 1},
            ],
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_get_cart_no_token(self, test_client: AsyncClient) -> None:
        """Test get cart in case there is no token."""

        response = await test_client.get(f"{AppConstants.API_V1_PREFIX}/carts/me/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_cart_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get cart in case user does not have appropriate scope."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/carts/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_cart_user_cart_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get cart in case cart is not found."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/carts/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Cart")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_add_product_to_the_cart(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "id": "65a7f143c064f4099808ad27",
                "quantity": 3,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_201_CREATED

        assert response.json() == {
            "id": "663ce924336962a87b140742",
            "user_id": "65844f12b6de26578d98c2c8",
            "products": [
                {
                    "id": "65d22fd0a83d80b9f0bd3e39",
                    "quantity": 2,
                },
                {"id": "65d22fd0a83d80b9f0bd3e42", "quantity": 1},
                {
                    "id": "65a7f143c064f4099808ad27",
                    "quantity": 3,
                },
            ],
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    async def test_add_product_to_the_cart_no_token(
        self, test_client: AsyncClient
    ) -> None:
        """Test add product to the cart in case there is no token."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "id": "65a7f143c064f4099808ad27",
                "quantity": 3,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_add_product_to_the_cart_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart in case user does not have appropriate scope."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "id": "65a7f143c064f4099808ad27",
                "quantity": 3,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.PRODUCTS)],
        indirect=True,
    )
    async def test_add_product_to_the_cart_cart_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart in case cart is not found."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "id": "65a7f143c064f4099808ad27",
                "quantity": 0,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Cart")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.PRODUCTS,
                MongoCollectionsEnum.CARTS,
            )
        ],
        indirect=True,
    )
    async def test_add_product_to_the_cart_another_user_cart(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart in case cart belongs to another user."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce958336962a87b140743/products/",
            json={
                "id": "65a7f143c064f4099808ad27",
                "quantity": 1,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.CART_ACCESS_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.PRODUCTS,
                MongoCollectionsEnum.CARTS,
            )
        ],
        indirect=True,
    )
    async def test_add_product_to_the_cart_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart in case request data is invalid."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "quantity": 0,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "_id"], "Field required"),
            ("greater_than", ["body", "quantity"], "Input should be greater than 0"),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS,)],
        indirect=True,
    )
    async def test_add_product_to_the_cart_product_does_not_exist(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart in case product does not exist."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "id": "65a7f143c064f4099808ad27",
                "quantity": 3,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Product")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    async def test_add_product_to_the_cart_product_is_not_available(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart in case product is not available."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "id": "65d22fd0a83d80b9f0bd3e38",
                "quantity": 3,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCT_ACCESS_DENIED
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    async def test_add_product_to_the_cart_product_is_added(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart in case product is already added."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "id": "65d22fd0a83d80b9f0bd3e39",
                "quantity": 1,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCT_IS_ALREADY_ADDED_TO_THE_CART
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    async def test_add_product_to_the_cart_validate_quantity(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test add product to the cart in case maximum quantity is exceeded."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/",
            json={
                "id": "65a7f143c064f4099808ad27",
                "quantity": 100,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.MAXIMUM_PRODUCT_QUANTITY_AVAILABLE
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_update_product_in_the_cart(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update product in the cart."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65d22fd0a83d80b9f0bd3e39/",
            json={
                "quantity": 4,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "id": "663ce924336962a87b140742",
            "user_id": "65844f12b6de26578d98c2c8",
            "products": [
                {
                    "id": "65d22fd0a83d80b9f0bd3e39",
                    "quantity": 4,
                },
                {"id": "65d22fd0a83d80b9f0bd3e42", "quantity": 1},
            ],
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    async def test_update_product_in_the_cart_no_token(
        self, test_client: AsyncClient
    ) -> None:
        """Test update product in the cart in case there is no token."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            json={
                "quantity": 3,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_product_in_the_cart_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test update product in the cart in case user does not have appropriate scope.
        """

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            json={
                "quantity": 3,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.PRODUCTS)],
        indirect=True,
    )
    async def test_update_product_in_the_cart_cart_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update product in the cart in case cart is not found."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            json={
                "quantity": 0,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Cart")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.PRODUCTS,
                MongoCollectionsEnum.CARTS,
            )
        ],
        indirect=True,
    )
    async def test_update_product_in_the_cart_another_user_cart(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update product in the cart in case cart belongs to another user."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce958336962a87b140743/products/65a7f143c064f4099808ad27/",
            json={
                "quantity": 0,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.CART_ACCESS_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.PRODUCTS,
                MongoCollectionsEnum.CARTS,
            )
        ],
        indirect=True,
    )
    async def test_update_product_in_the_cart_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update product in the cart in case request data is invalid."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65d22fd0a83d80b9f0bd3e39/",
            json={
                "quantity": -2,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("greater_than", ["body", "quantity"], "Input should be greater than 0"),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS,)],
        indirect=True,
    )
    async def test_update_product_in_the_cart_product_does_not_exist(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update product in the cart in case product does not exist."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            json={
                "quantity": 3,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Product")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    async def test_update_product_in_the_cart_product_is_not_available(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update product in the cart in case product is not available."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65d22fd0a83d80b9f0bd3e38/",
            json={
                "quantity": 3,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCT_ACCESS_DENIED
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    async def test_update_product_in_the_cart_product_is_not_added(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update product in the cart in case product is not added."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            json={
                "quantity": 1,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCT_IS_NOT_ADDED_TO_THE_CART
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    async def test_update_product_in_the_cart_validate_quantity(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update product in the cart in case maximum quantity is exceeded."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            json={
                "quantity": 100,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.MAXIMUM_PRODUCT_QUANTITY_AVAILABLE
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_delete_product_from_the_cart(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete product from the cart."""

        response = await test_client.delete(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65d22fd0a83d80b9f0bd3e39/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "id": "663ce924336962a87b140742",
            "user_id": "65844f12b6de26578d98c2c8",
            "products": [
                {"id": "65d22fd0a83d80b9f0bd3e42", "quantity": 1},
            ],
            "created_at": "2024-01-05T12:08:35.440000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    async def test_delete_product_from_the_cart_no_token(
        self, test_client: AsyncClient
    ) -> None:
        """Test delete product from the cart in case there is no token."""

        response = await test_client.delete(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_product_from_the_cart_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test delete product from the cart in case user does not have appropriate scope.
        """

        response = await test_client.delete(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.PRODUCTS)],
        indirect=True,
    )
    async def test_delete_product_from_the_cart_cart_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete product from the cart in case cart is not found."""

        response = await test_client.delete(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Cart")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.PRODUCTS,
                MongoCollectionsEnum.CARTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_product_from_the_cart_another_user_cart(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete product from the cart in case cart belongs to another user."""

        response = await test_client.delete(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce958336962a87b140743/products/65a7f143c064f4099808ad27/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.CART_ACCESS_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS,)],
        indirect=True,
    )
    async def test_delete_product_from_the_cart_product_does_not_exist(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete product from the cart in case product does not exist."""

        response = await test_client.delete(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Product")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_product_from_the_cart_product_is_not_available(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete product from the cart in case product is not available."""

        response = await test_client.delete(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65d22fd0a83d80b9f0bd3e38/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCT_ACCESS_DENIED
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.CARTS,
                MongoCollectionsEnum.PRODUCTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_product_from_the_cart_product_is_not_added(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete product from the cart in case product is not added."""

        response = await test_client.delete(
            f"{AppConstants.API_V1_PREFIX}/carts/663ce924336962a87b140742/products/65a7f143c064f4099808ad27/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PRODUCT_IS_NOT_ADDED_TO_THE_CART
        }
