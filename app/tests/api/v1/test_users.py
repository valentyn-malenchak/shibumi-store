"""Module that contains tests for users routes."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from freezegun import freeze_time
from httpx import AsyncClient
from jose import ExpiredSignatureError

from app.api.v1.constants import RolesEnum
from app.constants import HTTPErrorMessagesEnum, ValidationErrorMessagesEnum
from app.services.mongo.constants import MongoCollectionsEnum
from app.tests.api.v1 import BaseTest
from app.tests.constants import (
    CUSTOMER_USER,
    FAKE_USER,
    FROZEN_DATETIME,
    SHOP_SIDE_USER,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestUser(BaseTest):
    """Test class for users API endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_get_me(self, test_client: AsyncClient, arrange_db: None) -> None:
        """Test get me."""

        response = await test_client.get(
            "/users/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
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
            "roles": [RolesEnum.CUSTOMER.name],
            "created_at": "2023-12-30T13:25:43.895000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, test_client: AsyncClient) -> None:
        """Test get me in case there is no token."""

        response = await test_client.get("/users/me/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED.value}

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, test_client: AsyncClient) -> None:
        """Test get me in case access token is invalid."""

        response = await test_client.get(
            "/users/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_CREDENTIALS.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(side_effect=ExpiredSignatureError()))
    async def test_get_me_access_token_is_expired(
        self, test_client: AsyncClient
    ) -> None:
        """Test get me in case access token is expired."""

        response = await test_client.get(
            "/users/me/", headers={"Authorization": f"Bearer {TEST_JWT}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.EXPIRED_TOKEN.value}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=FAKE_USER))
    async def test_get_me_user_does_not_exist(self, test_client: AsyncClient) -> None:
        """
        Test get me in case user from access token does not exist.
        """

        response = await test_client.get(
            "/users/me/", headers={"Authorization": f"Bearer {TEST_JWT}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED.value}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_get_me_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get me in case user does not have appropriate scope."""

        response = await test_client.get(
            "/users/me/", headers={"Authorization": f"Bearer {TEST_JWT}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PERMISSION_DENIED.value
        }

    @pytest.mark.asyncio
    @freeze_time(FROZEN_DATETIME)
    async def test_create_users_unauthenticated_user_creates_customer_user(
        self, test_client: AsyncClient
    ) -> None:
        """Test create users in case unauthenticated user creates customer."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "Joe12345!",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert {
            key: value for key, value in response.json().items() if key != "id"
        } == {
            "first_name": "Joe",
            "last_name": "Smith",
            "patronymic_name": None,
            "username": "joe.smith",
            "email": "joe.smith@gmail.com",
            "phone_number": "+380980000000",
            "birthdate": "1997-12-07",
            "roles": [RolesEnum.CUSTOMER.name],
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_users_unauthenticated_user_creates_shop_side_user(
        self, test_client: AsyncClient
    ) -> None:
        """Test create users in case unauthenticated user creates shop side user."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "Joe12345!",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.SUPPORT.value],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ROLE_ACCESS_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    @freeze_time(FROZEN_DATETIME)
    async def test_create_users_shop_side_user_creates_multi_role_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create users in case shop side user creates multi-role user."""

        response = await test_client.post(
            "/users/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "Joe12345!",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [
                    RolesEnum.SUPPORT.value,
                    RolesEnum.CUSTOMER.value,
                    RolesEnum.CONTENT_MANAGER.value,
                    RolesEnum.ADMIN.value,
                ],
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert {
            key: value for key, value in response.json().items() if key != "id"
        } == {
            "first_name": "Joe",
            "last_name": "Smith",
            "patronymic_name": None,
            "username": "joe.smith",
            "email": "joe.smith@gmail.com",
            "phone_number": "+380980000000",
            "birthdate": "1997-12-07",
            "roles": [
                RolesEnum.SUPPORT.name,
                RolesEnum.CUSTOMER.name,
                RolesEnum.CONTENT_MANAGER.name,
                RolesEnum.ADMIN.name,
            ],
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_users_validate_json_data(
        self, test_client: AsyncClient
    ) -> None:
        """Test create users in case request json data is invalid."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": None,
                "email": "john.smith@gmail",
                "password": "Joe12345!",
                "phone_number": "+3809811",
                "birthdate": "1997-12-34",
                "roles": ["CEO"],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "username"], "Field required"),
            (
                "value_error",
                ["body", "email"],
                "value is not a valid email address: The part after the @-sign "
                "is not valid. It should have a period.",
            ),
            (
                "value_error",
                ["body", "phone_number"],
                "value is not a valid phone number",
            ),
            (
                "date_from_datetime_parsing",
                ["body", "birthdate"],
                "Input should be a valid date or datetime, day value is "
                "outside expected range",
            ),
            (
                "enum",
                ["body", "roles", 0],
                "Input should be 'Customer', 'Support', 'Warehouse stuff', "
                "'Content manager', 'Marketing manager' or 'Admin'",
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_users_short_password(self, test_client: AsyncClient) -> None:
        """Test create users in case password is short."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "joe12",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "string_too_short",
                ["body", "password"],
                ValidationErrorMessagesEnum.PASSWORD_MIN_LENGTH.value,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_users_password_with_no_digits(
        self, test_client: AsyncClient
    ) -> None:
        """Test create users in case password doesn't include digits."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "joejoejoe",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "string_without_digit",
                ["body", "password"],
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_DIGIT.value,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_users_password_with_no_lowercase_letters(
        self, test_client: AsyncClient
    ) -> None:
        """Test create users in case password doesn't include lowercase letters."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "JOE12345",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "string_without_lowercase_letters",
                ["body", "password"],
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_LOWERCASE_LETTER.value,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_users_password_with_no_uppercase_letters(
        self, test_client: AsyncClient
    ) -> None:
        """Test create users in case password doesn't include uppercase letters."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "joe12345",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "string_without_uppercase_letters",
                ["body", "password"],
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_UPPERCASE_LETTER.value,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_users_password_with_no_special_characters(
        self, test_client: AsyncClient
    ) -> None:
        """Test create users in case password doesn't include special characters."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "Joe12345",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "string_without_special_characters",
                ["body", "password"],
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_SPECIAL_CHARACTER.value,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_users_short_username(self, test_client: AsyncClient) -> None:
        """Test create users in case username is short."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe",
                "email": "joe.smith@gmail.com",
                "password": "Joe12345!~",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "string_too_short",
                ["body", "username"],
                ValidationErrorMessagesEnum.USERNAME_MIN_LENGTH.value,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_users_long_username(self, test_client: AsyncClient) -> None:
        """Test create users in case username is long."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith.joe.smith.joe.smith.joe.smith.joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "Joe12345!~",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "string_too_long",
                ["body", "username"],
                ValidationErrorMessagesEnum.USERNAME_MAX_LENGTH.value,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_users_username_contains_not_permitted_characters(
        self, test_client: AsyncClient
    ) -> None:
        """Test create users in case username contains not permitted characters."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe@smith",
                "email": "joe.smith@gmail.com",
                "password": "Joe12345!~",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "string_with_not_permitted_characters",
                ["body", "username"],
                ValidationErrorMessagesEnum.USERNAME_NOT_ALLOWED_CHARACTERS.value,
            ),
        ]

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_users_with_authorization_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test create users in case user has authorization and does not
        have appropriate scope.
        """

        response = await test_client.post(
            "/users/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "john.smith",
                "email": "john.smith@gmail.com",
                "password": "joe12345",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PERMISSION_DENIED.value
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_create_users_username_duplication(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create users in case user with such username is already exist."""

        response = await test_client.post(
            "/users/",
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "john.smith",
                "email": "john.smith@gmail.com",
                "password": "Joe12345!",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_FIELD_UNIQUENESS.value.format(
                entity="User", field="username"
            )
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    @freeze_time(FROZEN_DATETIME)
    async def test_update_users_customer_user_updates_self(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case customer user updates self with no role changes."""

        response = await test_client.patch(
            "/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith+1@gmail.com",
                "password": "John@1323",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert {key: value for key, value in response.json().items()} == {
            "id": "65844f12b6de26578d98c2c8",
            "first_name": "John",
            "last_name": "Smith",
            "patronymic_name": "Batman",
            "username": "john.smith",
            "email": "john.smith+1@gmail.com",
            "phone_number": "+380980000001",
            "birthdate": "1999-12-31",
            "roles": [RolesEnum.CUSTOMER.name],
            "created_at": "2023-12-30T13:25:43.895000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_update_users_customer_user_update_self_with_shop_side_roles(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case customer user requests shop side roles."""

        response = await test_client.patch(
            "/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith+1@gmail.com",
                "password": "John@1323",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER.value, RolesEnum.ADMIN.value],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ROLE_ACCESS_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    @freeze_time(FROZEN_DATETIME)
    async def test_update_users_shop_side_user_updates_self(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case shop side user updates self."""

        response = await test_client.patch(
            "/users/659bf67868d14b47475ec11c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "Anya",
                "last_name": "Schoen",
                "patronymic_name": None,
                "email": "anya.schoen+1@gmail.com",
                "password": "Anyaa@1323",
                "phone_number": "+380980004321",
                "birthdate": "1999-09-07",
                "roles": [
                    RolesEnum.WAREHOUSE_STUFF.value,
                    RolesEnum.ADMIN.value,
                    RolesEnum.CUSTOMER.value,
                ],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert {key: value for key, value in response.json().items()} == {
            "id": "659bf67868d14b47475ec11c",
            "first_name": "Anya",
            "last_name": "Schoen",
            "patronymic_name": None,
            "username": "anya.schoen",
            "email": "anya.schoen+1@gmail.com",
            "phone_number": "+380980004321",
            "birthdate": "1999-09-07",
            "roles": [
                RolesEnum.WAREHOUSE_STUFF.name,
                RolesEnum.ADMIN.name,
                RolesEnum.CUSTOMER.name,
            ],
            "created_at": "2024-01-08T13:25:43.895000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_update_users_validate_json_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case request json data is invalid."""

        response = await test_client.patch(
            "/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith@gmail",
                "password": "john_12!",
                "phone_number": "+3809800000013",
                "birthdate": "1999-12-35",
                "roles": ["CEO"],
            },
        )

        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "value_error",
                ["body", "email"],
                "value is not a valid email address: The part after the @-sign is not "
                "valid. It should have a period.",
            ),
            (
                "string_without_uppercase_letters",
                ["body", "password"],
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_UPPERCASE_LETTER.value,
            ),
            (
                "value_error",
                ["body", "phone_number"],
                "value is not a valid phone number",
            ),
            (
                "date_from_datetime_parsing",
                ["body", "birthdate"],
                "Input should be a valid date or datetime, day value is outside "
                "expected range",
            ),
            (
                "enum",
                ["body", "roles", 0],
                "Input should be 'Customer', 'Support', 'Warehouse stuff', "
                "'Content manager', 'Marketing manager' or 'Admin'",
            ),
        ]

    @pytest.mark.asyncio
    async def test_update_users_no_token(self, test_client: AsyncClient) -> None:
        """Test update users in case there is no token."""

        response = await test_client.patch(
            "/users/65844f12b6de26578d98c2c8/",
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith+1@gmail.com",
                "password": "john@1323",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED.value}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_update_users_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case user does not have appropriate scope."""

        response = await test_client.patch(
            "/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "john.smith",
                "email": "john.smith@gmail.com",
                "password": "Joe12345^",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PERMISSION_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_update_users_client_user_updates_another_client_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case client user updates another client user."""

        response = await test_client.patch(
            "/users/6598495fdf97a8e0d7e612ae/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith+1@gmail.com",
                "password": "john@1323",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.USER_ACCESS_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_update_users_client_user_updates_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case client user updates shop side user."""

        response = await test_client.patch(
            "/users/659c3528d71686302919981c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith+1@gmail.com",
                "password": "john@1323",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.USER_ACCESS_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_update_users_shop_side_user_updates_client_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case shop side user updates client user."""

        response = await test_client.patch(
            "/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith+1@gmail.com",
                "password": "john@1323",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.CLIENT_USER_ACCESS_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    @freeze_time(FROZEN_DATETIME)
    async def test_update_users_shop_side_user_updates_another_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case shop side user updates another shop side user."""

        response = await test_client.patch(
            "/users/659c3528d71686302919981c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "Frederique",
                "last_name": "Langosh",
                "patronymic_name": "Definitely not Batman",
                "email": "frederique.langosh@gmail.com",
                "password": "Freeedo@13223",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CONTENT_MANAGER.value],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "659c3528d71686302919981c",
            "first_name": "Frederique",
            "last_name": "Langosh",
            "patronymic_name": "Definitely not Batman",
            "username": "Frederique.Langosh",
            "email": "frederique.langosh@gmail.com",
            "phone_number": "+380980000001",
            "birthdate": "1999-12-31",
            "roles": ["CONTENT_MANAGER"],
            "created_at": "2024-01-08T13:56:43.895000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_update_users_deleted_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case user is deleted."""

        response = await test_client.patch(
            "/users/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "Frederique",
                "last_name": "Langosh",
                "patronymic_name": "Definitely not Batman",
                "email": "frederique.langosh@gmail.com",
                "password": "Freeedo@13223",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CONTENT_MANAGER.value],
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.value.format(
                entity="User"
            )
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_update_users_invalid_identifier(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update users in case of invalid identifier."""

        response = await test_client.patch(
            "/users/invalid-group-id/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith+1@gmail.com",
                "password": "john@1323",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER.value],
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_IDENTIFIER.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_client_user_deletes_self(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users if case client user deletes self."""

        response = await test_client.delete(
            "/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_shop_side_user_deletes_self(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users in case shop side user deletes self."""

        response = await test_client.delete(
            "/users/659bf67868d14b47475ec11c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_users_no_token(self, test_client: AsyncClient) -> None:
        """Test delete users in case there is no token."""

        response = await test_client.delete("/users/65844f12b6de26578d98c2c8/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED.value}

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users in case user does not have appropriate scope."""

        response = await test_client.delete(
            "/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PERMISSION_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_client_user_deletes_another_client_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users in case client user deletes another client user."""

        response = await test_client.delete(
            "/users/6598495fdf97a8e0d7e612ae/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.USER_ACCESS_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_client_user_deletes_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users in case client user deletes shop side user."""

        response = await test_client.delete(
            "/users/659c3528d71686302919981c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.USER_ACCESS_DENIED.value
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_shop_side_user_deletes_client_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users in case shop side user deletes client user."""

        response = await test_client.delete(
            "/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_shop_side_user_deletes_another_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users in case shop side user deletes another shop side user."""

        response = await test_client.delete(
            "/users/659c3528d71686302919981c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_deleted_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users in case user is deleted."""

        response = await test_client.delete(
            "/users/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.value.format(
                entity="User"
            )
        }

    @pytest.mark.asyncio
    @patch("jose.jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize("arrange_db", [MongoCollectionsEnum.USERS], indirect=True)
    async def test_delete_users_invalid_identifier(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete users in case of invalid identifier."""

        response = await test_client.delete(
            "/users/invalid-group-id/", headers={"Authorization": f"Bearer {TEST_JWT}"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_IDENTIFIER.value
        }
