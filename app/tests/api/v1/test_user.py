"""Module that contains tests for user routes."""

from unittest.mock import MagicMock, Mock, patch

import jwt
import pytest
from fastapi import status
from freezegun import freeze_time
from httpx import AsyncClient
from sendgrid import SendGridException  # type: ignore
from tenacity import RetryError, wait_none

from app.api.v1.constants import RolesEnum
from app.constants import (
    HTTPErrorMessagesEnum,
    ValidationErrorMessagesEnum,
)
from app.services.mongo.constants import MongoCollectionsEnum
from app.services.send_grid.service import SendGridService
from app.settings import SETTINGS
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    CUSTOMER_USER,
    FAKE_USER,
    FROZEN_DATETIME,
    NOT_VERIFIED_EMAIL_USER,
    REDIS_VERIFICATION_TOKEN,
    SHOP_SIDE_USER,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestUser(BaseAPITest):
    """Test class for user APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_me(self, test_client: AsyncClient, arrange_db: None) -> None:
        """Test get me."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/me/",
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
            "email_verified": True,
            "phone_number": "+380981111111",
            "birthdate": "1998-01-01",
            "roles": [RolesEnum.CUSTOMER],
            "deleted": False,
            "created_at": "2023-12-30T13:25:43.895000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, test_client: AsyncClient) -> None:
        """Test get me in case there is no token."""

        response = await test_client.get(f"{SETTINGS.APP_API_V1_PREFIX}/users/me/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, test_client: AsyncClient) -> None:
        """Test get me in case access token is invalid."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.INVALID_CREDENTIALS}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(side_effect=jwt.ExpiredSignatureError()))
    async def test_get_me_access_token_is_expired(
        self, test_client: AsyncClient
    ) -> None:
        """Test get me in case access token is expired."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.EXPIRED_TOKEN}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=FAKE_USER))
    async def test_get_me_user_does_not_exist(self, test_client: AsyncClient) -> None:
        """Test get me in case user from access token does not exist."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_me_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get me in case user does not have appropriate scope."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @patch("jwt.decode", Mock(return_value=NOT_VERIFIED_EMAIL_USER))
    async def test_get_me_user_email_is_not_verified(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get me in case user email is not verified."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/me/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.EMAIL_IS_NOT_VERIFIED
        }

    @pytest.mark.asyncio
    @freeze_time(FROZEN_DATETIME)
    async def test_create_user_unauthenticated_user_creates_customer_user(
        self,
        test_client: AsyncClient,
        redis_setex_mock: MagicMock,
        send_grid_send_mock: MagicMock,
    ) -> None:
        """Test create user in case unauthenticated user creates customer."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "?%J4Tvhb",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert redis_setex_mock.call_count == 1
        assert send_grid_send_mock.call_count == 1

        assert response.status_code == status.HTTP_201_CREATED
        assert self._exclude_fields(response.json(), exclude_keys=["id"]) == {
            "first_name": "Joe",
            "last_name": "Smith",
            "patronymic_name": None,
            "username": "joe.smith",
            "email": "joe.smith@gmail.com",
            "email_verified": False,
            "phone_number": "+380980000000",
            "birthdate": "1997-12-07",
            "roles": [RolesEnum.CUSTOMER],
            "deleted": False,
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_user_unauthenticated_user_creates_shop_side_user(
        self, test_client: AsyncClient
    ) -> None:
        """Test create user in case unauthenticated user creates shop side user."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "?%J4Tvhb",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.SUPPORT],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="role")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_create_user_shop_side_user_creates_multi_role_user(
        self,
        test_client: AsyncClient,
        arrange_db: None,
        redis_setex_mock: MagicMock,
        send_grid_send_mock: MagicMock,
    ) -> None:
        """Test create user in case shop side user creates multi-role user."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "?%J4Tvhb",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [
                    RolesEnum.SUPPORT,
                    RolesEnum.CUSTOMER,
                    RolesEnum.CONTENT_MANAGER,
                    RolesEnum.ADMIN,
                ],
            },
        )

        assert redis_setex_mock.call_count == 1
        assert send_grid_send_mock.call_count == 1

        assert response.status_code == status.HTTP_201_CREATED
        assert self._exclude_fields(response.json(), exclude_keys=["id"]) == {
            "first_name": "Joe",
            "last_name": "Smith",
            "patronymic_name": None,
            "username": "joe.smith",
            "email": "joe.smith@gmail.com",
            "email_verified": False,
            "phone_number": "+380980000000",
            "birthdate": "1997-12-07",
            "roles": [
                RolesEnum.SUPPORT,
                RolesEnum.CUSTOMER,
                RolesEnum.CONTENT_MANAGER,
                RolesEnum.ADMIN,
            ],
            "deleted": False,
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_user_validate_data(self, test_client: AsyncClient) -> None:
        """Test create user in case request data is invalid."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": None,
                "email": "john.smith@gmail",
                "password": "?%J4Tvhb",
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
                "Input should be 'customer', 'support', 'warehouse_stuff', "
                "'content_manager', 'marketing_manager' or 'admin'",
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_user_short_password(self, test_client: AsyncClient) -> None:
        """Test create user in case password is short."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "joe12",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
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
                ValidationErrorMessagesEnum.PASSWORD_MIN_LENGTH,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_user_password_with_no_digits(
        self, test_client: AsyncClient
    ) -> None:
        """Test create user in case password doesn't include digits."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "joejoejoe",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
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
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_DIGIT,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_user_password_with_no_lowercase_letters(
        self, test_client: AsyncClient
    ) -> None:
        """Test create user in case password doesn't include lowercase letters."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "JOE12345",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
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
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_LOWERCASE_LETTER,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_user_password_with_no_uppercase_letters(
        self, test_client: AsyncClient
    ) -> None:
        """Test create user in case password doesn't include uppercase letters."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "joe12345",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
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
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_UPPERCASE_LETTER,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_user_password_with_no_special_characters(
        self, test_client: AsyncClient
    ) -> None:
        """Test create user in case password doesn't include special characters."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "Joe12345",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
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
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_SPECIAL_CHARACTER,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_user_short_username(self, test_client: AsyncClient) -> None:
        """Test create user in case username is short."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe",
                "email": "joe.smith@gmail.com",
                "password": "?%J4Tvhb",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
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
                ValidationErrorMessagesEnum.USERNAME_MIN_LENGTH,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_user_long_username(self, test_client: AsyncClient) -> None:
        """Test create user in case username is long."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe.smith.joe.smith.joe.smith.joe.smith.joe.smith",
                "email": "joe.smith@gmail.com",
                "password": "?%J4Tvhb",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
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
                ValidationErrorMessagesEnum.USERNAME_MAX_LENGTH,
            ),
        ]

    @pytest.mark.asyncio
    async def test_create_user_username_contains_not_permitted_characters(
        self, test_client: AsyncClient
    ) -> None:
        """Test create user in case username contains not permitted characters."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "Joe",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "joe@smith",
                "email": "joe.smith@gmail.com",
                "password": "?%J4Tvhb",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
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
                ValidationErrorMessagesEnum.USERNAME_NOT_ALLOWED_CHARACTERS,
            ),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_user_with_authorization_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test create user in case user has authorization and does not
        have appropriate scope.
        """

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "john.smith",
                "email": "john.smith@gmail.com",
                "password": "?%J4Tvhb",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_user_username_duplication(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create user in case user with such username is already exist."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "john.smith",
                "email": "john.smith@gmail.com",
                "password": "?%J4Tvhb",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_FIELD_UNIQUENESS.format(
                entity="User", field="username"
            )
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_update_user_customer_user_updates_self(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case customer user updates self with no role changes."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith@gmail.com",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "65844f12b6de26578d98c2c8",
            "first_name": "John",
            "last_name": "Smith",
            "patronymic_name": "Batman",
            "username": "john.smith",
            "email": "john.smith@gmail.com",
            "email_verified": True,
            "phone_number": "+380980000001",
            "birthdate": "1999-12-31",
            "roles": [RolesEnum.CUSTOMER],
            "deleted": False,
            "created_at": "2023-12-30T13:25:43.895000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_customer_user_update_self_with_shop_side_roles(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case customer user requests shop side roles."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith@gmail.com",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER, RolesEnum.ADMIN],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="role")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_update_user_shop_side_user_updates_self(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case shop side user updates self."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659bf67868d14b47475ec11c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "Anya",
                "last_name": "Schoen",
                "patronymic_name": None,
                "email": "anya_schoen@gmail.com",
                "phone_number": "+380980004321",
                "birthdate": "1999-09-07",
                "roles": [
                    RolesEnum.WAREHOUSE_STUFF,
                    RolesEnum.ADMIN,
                    RolesEnum.CUSTOMER,
                ],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "659bf67868d14b47475ec11c",
            "first_name": "Anya",
            "last_name": "Schoen",
            "patronymic_name": None,
            "username": "anya.schoen",
            "email": "anya_schoen@gmail.com",
            "email_verified": True,
            "phone_number": "+380980004321",
            "birthdate": "1999-09-07",
            "roles": [
                RolesEnum.WAREHOUSE_STUFF,
                RolesEnum.ADMIN,
                RolesEnum.CUSTOMER,
            ],
            "deleted": False,
            "created_at": "2024-01-08T13:25:43.895000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_update_user_email_change(
        self,
        test_client: AsyncClient,
        arrange_db: None,
        redis_setex_mock: MagicMock,
        send_grid_send_mock: MagicMock,
    ) -> None:
        """Test update user in case email is changed."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith+1@gmail.com",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert redis_setex_mock.call_count == 1
        assert send_grid_send_mock.call_count == 1

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "65844f12b6de26578d98c2c8",
            "first_name": "John",
            "last_name": "Smith",
            "patronymic_name": "Batman",
            "username": "john.smith",
            "email": "john.smith+1@gmail.com",
            "email_verified": False,
            "phone_number": "+380980000001",
            "birthdate": "1999-12-31",
            "roles": [RolesEnum.CUSTOMER],
            "deleted": False,
            "created_at": "2023-12-30T13:25:43.895000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_validate_json_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case request json data is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/invalid-identifier/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "email": "john.smith@gmail.com",
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
                "object_id",
                ["path", "user_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
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
                "Input should be 'customer', 'support', 'warehouse_stuff', "
                "'content_manager', 'marketing_manager' or 'admin'",
            ),
        ]

    @pytest.mark.asyncio
    async def test_update_user_no_token(self, test_client: AsyncClient) -> None:
        """Test update user in case there is no token."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case user does not have appropriate scope."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": None,
                "username": "john.smith",
                "phone_number": "+380980000000",
                "birthdate": "1997-12-07",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_client_user_updates_another_client_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case client user updates another client user."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/6598495fdf97a8e0d7e612ae/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="user")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_client_user_updates_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case client user updates shop side user."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659c3528d71686302919981c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="user")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_shop_side_user_updates_client_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case shop side user updates client user."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "John",
                "last_name": "Smith",
                "patronymic_name": "Batman",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CUSTOMER],
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(
                destination="client user"
            )
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_update_user_shop_side_user_updates_another_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case shop side user updates another shop side user."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659c3528d71686302919981c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "Frederique",
                "last_name": "Langosh",
                "patronymic_name": "Definitely not Batman",
                "email": "frederique.langosh@gmail.com",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CONTENT_MANAGER],
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
            "email_verified": True,
            "phone_number": "+380980000001",
            "birthdate": "1999-12-31",
            "roles": [RolesEnum.CONTENT_MANAGER],
            "deleted": False,
            "created_at": "2024-01-08T13:56:43.895000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_deleted_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user in case user is deleted."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
            json={
                "first_name": "Frederique",
                "last_name": "Langosh",
                "patronymic_name": "Definitely not Batman",
                "phone_number": "+380980000001",
                "birthdate": "1999-12-31",
                "roles": [RolesEnum.CONTENT_MANAGER],
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_client_user_deletes_self(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user if case client user deletes self."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_shop_side_user_deletes_self(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user in case shop side user deletes self."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659bf67868d14b47475ec11c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_user_no_token(self, test_client: AsyncClient) -> None:
        """Test delete user in case there is no token."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user in case user does not have appropriate scope."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_client_user_deletes_another_client_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user in case client user deletes another client user."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/6598495fdf97a8e0d7e612ae/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="user")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_client_user_deletes_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user in case client user deletes shop side user."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659c3528d71686302919981c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="user")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_shop_side_user_deletes_client_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user in case shop side user deletes client user."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_shop_side_user_deletes_another_shop_side_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user in case shop side user deletes another shop side user."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659c3528d71686302919981c/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_deleted_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user in case user is deleted."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_user_invalid_identifier(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete user in case of invalid identifier."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/invalid-group-id/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "object_id",
                ["path", "user_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
            )
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_user(self, test_client: AsyncClient, arrange_db: None) -> None:
        """Test get user."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "659ac89bfe61d8332f6be4c4",
            "first_name": "Sheila",
            "last_name": "Fahey",
            "patronymic_name": None,
            "username": "sheila.fahey",
            "email": "sheila.fahey@gmail.com",
            "email_verified": True,
            "phone_number": "+111111111114",
            "birthdate": "1994-11-14",
            "roles": ["content_manager"],
            "deleted": True,
            "created_at": "2024-01-07T13:25:43.895000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_get_user_no_token(self, test_client: AsyncClient) -> None:
        """Test get user in case there is no token."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659ac89bfe61d8332f6be4c4/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_user_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get user in case user does not have a scope."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659ac89bfe61d8332f6be4c4/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_user_invalid_identifier(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get user in case of invalid identifier."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/invalid-group-id/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "object_id",
                ["path", "user_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
            )
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_user_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get user in case of identifier is valid, but there is no such user."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/6598495fdf97a8e0d7e612aa/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_users_list(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get users list."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            params={"page": 1, "page_size": 3},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "65844f12b6de26578d98c2c8",
                    "first_name": "John",
                    "last_name": "Smith",
                    "patronymic_name": None,
                    "username": "john.smith",
                    "email": "john.smith@gmail.com",
                    "email_verified": True,
                    "phone_number": "+380981111111",
                    "birthdate": "1998-01-01",
                    "roles": ["customer"],
                    "deleted": False,
                    "created_at": "2023-12-30T13:25:43.895000",
                    "updated_at": None,
                },
                {
                    "id": "6598495fdf97a8e0d7e612ae",
                    "first_name": "Bruce",
                    "last_name": "Wayne",
                    "patronymic_name": None,
                    "username": "bruce.wayne",
                    "email": "bruce_wayne@gmail.com",
                    "email_verified": True,
                    "phone_number": "+111111111111",
                    "birthdate": "1939-03-30",
                    "roles": ["customer"],
                    "deleted": False,
                    "created_at": "2023-11-11T13:25:43.895000",
                    "updated_at": None,
                },
                {
                    "id": "659ac89bfe61d8332f6be4c4",
                    "first_name": "Sheila",
                    "last_name": "Fahey",
                    "patronymic_name": None,
                    "username": "sheila.fahey",
                    "email": "sheila.fahey@gmail.com",
                    "email_verified": True,
                    "phone_number": "+111111111114",
                    "birthdate": "1994-11-14",
                    "roles": ["content_manager"],
                    "deleted": True,
                    "created_at": "2024-01-07T13:25:43.895000",
                    "updated_at": None,
                },
            ],
            "total": 7,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_users_list_with_filters(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get users list with filters."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            params={
                "page": 1,
                "page_size": 1,
                "deleted": False,
                "roles": ["support", "warehouse_stuff"],
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "659bf67868d14b47475ec11c",
                    "first_name": "Anya",
                    "last_name": "Schoen",
                    "patronymic_name": None,
                    "username": "anya.schoen",
                    "email": "anya_schoen@gmail.com",
                    "email_verified": True,
                    "phone_number": "+123111111111",
                    "birthdate": "1994-08-04",
                    "roles": ["support", "content_manager"],
                    "deleted": False,
                    "created_at": "2024-01-08T13:25:43.895000",
                    "updated_at": None,
                }
            ],
            "total": 2,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_users_list_with_search(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get users list with search."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            params={"page": 1, "page_size": 1, "search": "anya"},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "659bf67868d14b47475ec11c",
                    "first_name": "Anya",
                    "last_name": "Schoen",
                    "patronymic_name": None,
                    "username": "anya.schoen",
                    "email": "anya_schoen@gmail.com",
                    "email_verified": True,
                    "phone_number": "+123111111111",
                    "birthdate": "1994-08-04",
                    "roles": ["support", "content_manager"],
                    "deleted": False,
                    "created_at": "2024-01-08T13:25:43.895000",
                    "updated_at": None,
                }
            ],
            "total": 1,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_users_list_with_sorting(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get users list with sorting."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            params={
                "page": 1,
                "page_size": 1,
                "sort_by": "first_name",
                "sort_order": "desc",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "id": "659ac89bfe61d8332f6be4c4",
                    "first_name": "Sheila",
                    "last_name": "Fahey",
                    "patronymic_name": None,
                    "username": "sheila.fahey",
                    "email": "sheila.fahey@gmail.com",
                    "email_verified": True,
                    "phone_number": "+111111111114",
                    "birthdate": "1994-11-14",
                    "roles": ["content_manager"],
                    "deleted": True,
                    "created_at": "2024-01-07T13:25:43.895000",
                    "updated_at": None,
                }
            ],
            "total": 7,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_users_list_validate_query_params(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get users list in case query parameters are invalid."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            params={
                "roles": ["Any"],
                "deleted": "yes",
                "sort_by": "random_field",
                "sort_order": "any",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "enum",
                ["query", "roles", 0],
                "Input should be 'customer', 'support', 'warehouse_stuff', "
                "'content_manager', 'marketing_manager' or 'admin'",
            ),
            ("enum", ["query", "sort_order"], "Input should be 'asc' or 'desc'"),
            ("missing", ["query", "page"], "Field required"),
            ("missing", ["query", "page_size"], "Field required"),
        ]

    @pytest.mark.asyncio
    async def test_get_users_list_no_token(self, test_client: AsyncClient) -> None:
        """Test get users list in case there is no token."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            params={"page": 1, "page_size": 20},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_users_list_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get users list in case user does not have a scope."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_password(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user password."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/password/",
            json={
                "old_password": "?%J4Tvhb",
                "new_password": "NewP@ssw0rd",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_update_user_password_no_token(
        self, test_client: AsyncClient
    ) -> None:
        """Test update user password in case there is no token."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/password/",
            json={
                "old_password": "?%J4Tvhb",
                "new_password": "NewP@ssw0rd",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_password_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user password in case user does not have a scope."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/password/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_password_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user password in case request data is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/invalid-group-id/password/",
            json={
                "new_password": "1234!",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            (
                "object_id",
                ["path", "user_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
            ),
            (
                "object_id",
                ["path", "user_id"],
                ValidationErrorMessagesEnum.INVALID_IDENTIFIER,
            ),
            ("missing", ["body", "old_password"], "Field required"),
            (
                "string_too_short",
                ["body", "new_password"],
                "Password must contain at least eight characters.",
            ),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_password_user_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test update user password in case of identifier is valid,
        but there is no such user.
        """

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/6598495fdf97a8e0d7e612aa/password/",
            json={
                "old_password": "?%J4Tvhb",
                "new_password": "J0hn1234!@~",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_password_for_another_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user password in case user updates for another user."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/659bf67868d14b47475ec11c/password/",
            json={
                "old_password": "?%J4Tvhb",
                "new_password": "J0hn1234!@~",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="user")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_user_password_invalid_old_password(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update user password in case old password is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/65844f12b6de26578d98c2c8/password/",
            json={
                "old_password": "John1234",
                "new_password": "J0hn1234!@~",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.PASSWORD_DOES_NOT_MATCH
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_request_reset_user_password(
        self,
        test_client: AsyncClient,
        arrange_db: None,
        redis_setex_mock: MagicMock,
        send_grid_send_mock: MagicMock,
    ) -> None:
        """Test request reset user password."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/reset-password/"
        )

        assert redis_setex_mock.call_count == 1
        assert send_grid_send_mock.call_count == 1

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_request_reset_user_password_user_is_not_found(
        self, test_client: AsyncClient
    ) -> None:
        """Test request reset user password in case user with username is not found."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/reset-password/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_request_reset_user_password_user_is_deleted(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test request reset user password in case user is deleted."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/sheila.fahey/reset-password/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @pytest.mark.parametrize(
        "send_grid_send_mock", [SendGridException()], indirect=True
    )
    async def test_request_reset_user_password_send_grid_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        test_client: AsyncClient,
        arrange_db: None,
        redis_setex_mock: MagicMock,
        send_grid_send_mock: MagicMock,
    ) -> None:
        """Test request reset user password in case some error in SendGrid."""

        # Skip waiting between attempts
        monkeypatch.setattr(SendGridService.send.retry, "wait", wait_none())  # type: ignore

        with pytest.raises(RetryError):
            await test_client.post(
                f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/reset-password/"
            )

        assert redis_setex_mock.call_count == 1
        assert send_grid_send_mock.call_count == 3  # noqa: PLR2004

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @pytest.mark.parametrize(
        "redis_get_mock",
        [REDIS_VERIFICATION_TOKEN],
        indirect=True,
    )
    async def test_reset_user_password(
        self,
        test_client: AsyncClient,
        arrange_db: None,
        redis_get_mock: MagicMock,
        redis_delete_mock: MagicMock,
    ) -> None:
        """Test reset user password."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/reset-password/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
                "new_password": "J0hn1234!@~",
            },
        )

        assert redis_get_mock.call_count == 1
        assert redis_delete_mock.call_count == 1

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_reset_user_password_user_is_not_found(
        self, test_client: AsyncClient
    ) -> None:
        """Test reset user password in case user with username is not found."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/reset-password/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
                "new_password": "J0hn1234!@~",
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_reset_user_password_user_is_deleted(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test reset user password in case user is deleted."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/sheila.fahey/reset-password/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
                "new_password": "J0hn1234!@~",
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_reset_user_password_validate_json_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test reset user password in case request json data is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/reset-password/",
            json={"new_password": "John1234"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "token"], "Field required"),
            (
                "string_without_special_characters",
                ["body", "new_password"],
                "Password must contain at least one special character.",
            ),
        ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_reset_user_password_token_is_expired(
        self, test_client: AsyncClient, arrange_db: None, redis_get_mock: MagicMock
    ) -> None:
        """Test reset user password in case token is expired."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/reset-password/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
                "new_password": "J0hn1234!@~",
            },
        )

        assert redis_get_mock.call_count == 1

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_RESET_PASSWORD_TOKEN
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @pytest.mark.parametrize(
        "redis_get_mock",
        [REDIS_VERIFICATION_TOKEN],
        indirect=True,
    )
    async def test_reset_user_password_token_is_invalid(
        self, test_client: AsyncClient, arrange_db: None, redis_get_mock: MagicMock
    ) -> None:
        """Test reset user password in case token is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/reset-password/",
            json={
                "token": "U66kv5LtukldDDSANUe",
                "new_password": "J0hn1234!@~",
            },
        )

        assert redis_get_mock.call_count == 1

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_RESET_PASSWORD_TOKEN
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_request_verify_user_email(
        self,
        test_client: AsyncClient,
        arrange_db: None,
        redis_setex_mock: MagicMock,
        send_grid_send_mock: MagicMock,
    ) -> None:
        """Test request verify user email."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/lila.legro/verify-email/"
        )

        assert redis_setex_mock.call_count == 1
        assert send_grid_send_mock.call_count == 1

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_request_verify_user_email_user_is_not_found(
        self, test_client: AsyncClient
    ) -> None:
        """Test request verify user email in case user with username is not found."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/lila.legro/verify-email/"
        )

        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_request_verify_user_email_user_is_deleted(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test request verify user email in case user is deleted."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/sheila.fahey/verify-email/"
        )

        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_request_verify_user_email_user_email_is_verified(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test request verify user email in case user email is already verified."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/verify-email/"
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.EMAIL_IS_ALREADY_VERIFIED
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @pytest.mark.parametrize(
        "send_grid_send_mock", [SendGridException()], indirect=True
    )
    async def test_request_verify_user_email_send_grid_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        test_client: AsyncClient,
        arrange_db: None,
        redis_setex_mock: MagicMock,
        send_grid_send_mock: MagicMock,
    ) -> None:
        """Test request verify user email in case some error in SendGrid."""

        # Skip waiting between attempts
        monkeypatch.setattr(SendGridService.send.retry, "wait", wait_none())  # type: ignore

        with pytest.raises(RetryError):
            await test_client.post(
                f"{SETTINGS.APP_API_V1_PREFIX}/users/lila.legro/verify-email/"
            )

        assert redis_setex_mock.call_count == 1
        assert send_grid_send_mock.call_count == 3  # noqa: PLR2004

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @pytest.mark.parametrize(
        "redis_get_mock",
        [REDIS_VERIFICATION_TOKEN],
        indirect=True,
    )
    async def test_verify_user_email(
        self,
        test_client: AsyncClient,
        arrange_db: None,
        redis_get_mock: MagicMock,
        redis_delete_mock: MagicMock,
    ) -> None:
        """Test verify user email."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/lila.legro/verify-email/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
            },
        )

        assert redis_get_mock.call_count == 1
        assert redis_delete_mock.call_count == 1

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_verify_user_email_user_is_not_found(
        self, test_client: AsyncClient
    ) -> None:
        """Test verify user email in case user with username is not found."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/lila.legro/verify-email/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_verify_user_email_user_is_deleted(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test verify user email in case user is deleted."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/sheila.fahey/verify-email/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User")
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_verify_user_email_user_email_is_verified(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test verify user email in case user email is already verified."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/john.smith/verify-email/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
            },
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.EMAIL_IS_ALREADY_VERIFIED
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_verify_user_email_validate_json_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test verify user email in case request json data is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/lila.legro/verify-email/",
            json={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "token"], "Field required"),
        ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_verify_user_email_token_is_expired(
        self, test_client: AsyncClient, arrange_db: None, redis_get_mock: MagicMock
    ) -> None:
        """Test verify user email in case token is expired."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/lila.legro/verify-email/",
            json={
                "token": "U66kv5LtukldDDSANUeAefQmjmeZuIcxC2lwiMUK6ec",
            },
        )

        assert redis_get_mock.call_count == 1

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_EMAIL_VERIFICATION_TOKEN
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    @pytest.mark.parametrize(
        "redis_get_mock",
        [REDIS_VERIFICATION_TOKEN],
        indirect=True,
    )
    async def test_verify_user_email_token_is_invalid(
        self, test_client: AsyncClient, arrange_db: None, redis_get_mock: MagicMock
    ) -> None:
        """Test verify user email in case token is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/users/lila.legro/verify-email/",
            json={
                "token": "U66kv5LtukldDDSANUe",
            },
        )

        assert redis_get_mock.call_count == 1

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.INVALID_EMAIL_VERIFICATION_TOKEN
        }
