"""Module that contains tests for comments routes."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.constants import (
    HTTPErrorMessagesEnum,
)
from app.services.mongo.constants import MongoCollectionsEnum
from app.settings import SETTINGS
from app.tests.api.v1 import BaseAPITest
from app.tests.constants import (
    CUSTOMER_USER,
    FROZEN_DATETIME,
    SHOP_SIDE_USER,
    TEST_JWT,
    USER_NO_SCOPES,
)


class TestComment(BaseAPITest):
    """Test class for comment APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_get_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get comment."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "666af9246aba47cfb60efb37",
            "body": "seventh product message",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "user_id": "65844f12b6de26578d98c2c8",
            "parent_comment_id": "666af91a6aba47cfb60efb36",
            "path": "/666af91a6aba47cfb60efb36/666af9246aba47cfb60efb37",
            "upvotes": 0,
            "downvotes": 0,
            "deleted": False,
            "created_at": "2024-06-13T13:50:28.453000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_get_comment_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get comment in case there is no token."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "666af9246aba47cfb60efb37",
            "body": "seventh product message",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "user_id": "65844f12b6de26578d98c2c8",
            "parent_comment_id": "666af91a6aba47cfb60efb36",
            "path": "/666af91a6aba47cfb60efb36/666af9246aba47cfb60efb37",
            "upvotes": 0,
            "downvotes": 0,
            "deleted": False,
            "created_at": "2024-06-13T13:50:28.453000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_comment_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get comment in case user does not have appropriate scope."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS,)],
        indirect=True,
    )
    async def test_get_comment_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get comment in case comment is not found."""

        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Comment")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.THREADS,
            )
        ],
        indirect=True,
    )
    async def test_create_comment_root_comment(
        self, test_client: AsyncClient, arrange_db: None, datetime_now_mock: MagicMock
    ) -> None:
        """Test create comment in case of root comment."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/",
            json={
                "thread_id": "6669b5634cef83e11dbc7abf",
                "body": "some product question 1",
                "parent_comment_id": None,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert self._exclude_fields(response.json(), exclude_keys=["id"]) == {
            "body": "some product question 1",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "user_id": "65844f12b6de26578d98c2c8",
            "parent_comment_id": None,
            "path": f"/{response.json()["id"]}",
            "upvotes": 0,
            "downvotes": 0,
            "deleted": False,
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.THREADS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_create_comment_with_parent(
        self, test_client: AsyncClient, arrange_db: None, datetime_now_mock: MagicMock
    ) -> None:
        """Test create comment in case comment has parent."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/",
            json={
                "thread_id": "6669b5634cef83e11dbc7abf",
                "body": "some product question 2",
                "parent_comment_id": "666af8cb6aba47cfb60efb33",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert self._exclude_fields(response.json(), exclude_keys=["id"]) == {
            "body": "some product question 2",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "user_id": "65844f12b6de26578d98c2c8",
            "parent_comment_id": "666af8cb6aba47cfb60efb33",
            "path": f"/666af8ae6aba47cfb60efb31/666af8cb6aba47cfb60efb33/"
            f"{response.json()["id"]}",
            "upvotes": 0,
            "downvotes": 0,
            "deleted": False,
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_comment_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create comment in case there is no token."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/",
            json={
                "thread_id": "6669b5634cef83e11dbc7abf",
                "body": "some product question 1",
                "parent_comment_id": None,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_comment_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create comment in case user does not have appropriate scope."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/",
            json={
                "thread_id": "6669b5634cef83e11dbc7abf",
                "body": "some product question 1",
                "parent_comment_id": None,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_comment_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create comment in case request data is invalid."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/",
            json={"parent_comment_id": 123},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "thread_id"], "Field required"),
            ("missing", ["body", "body"], "Field required"),
            ("object_id", ["body", "parent_comment_id"], "Invalid object identifier."),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_comment_thread_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create comment in case thread is not found."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/",
            json={
                "thread_id": "6669b5634cef83e11dbc7abf",
                "body": "some product question 1",
                "parent_comment_id": None,
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Thread")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.THREADS)],
        indirect=True,
    )
    async def test_create_comment_parent_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create comment in case parent comment is not found."""

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/",
            json={
                "thread_id": "6669b5634cef83e11dbc7abf",
                "body": "some product question 2",
                "parent_comment_id": "666af8cb6aba47cfb60efb33",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Comment")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.THREADS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_create_comment_parent_comment_is_not_related_to_thread(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test create comment in case parent comment does not belong to thread.
        """

        response = await test_client.post(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/",
            json={
                "thread_id": "6669b5de4cef83e11dbc7ac2",
                "body": "some product question 1",
                "parent_comment_id": "666af8cb6aba47cfb60efb33",
            },
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITIES_ARE_NOT_RELATED.format(
                child_entity="Comment", parent_entity="thread"
            ),
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_update_comment(
        self, test_client: AsyncClient, arrange_db: None, datetime_now_mock: MagicMock
    ) -> None:
        """Test update comment."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            json={"body": "edited seventh product message"},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "666af9246aba47cfb60efb37",
            "body": "edited seventh product message",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "user_id": "65844f12b6de26578d98c2c8",
            "parent_comment_id": "666af91a6aba47cfb60efb36",
            "path": "/666af91a6aba47cfb60efb36/666af9246aba47cfb60efb37",
            "upvotes": 0,
            "downvotes": 0,
            "deleted": False,
            "created_at": "2024-06-13T13:50:28.453000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    async def test_update_comment_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update comment in case there is no token."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            json={"body": "edited seventh product message"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_comment_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update comment in case user does not have appropriate scope."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            json={"body": "edited seventh product message"},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_update_comment_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update comment in case request data is invalid."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            json={},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "body"], "Field required"),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS,)],
        indirect=True,
    )
    async def test_update_comment_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update comment in case comment is not found."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            json={},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Comment")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.COMMENTS)],
        indirect=True,
    )
    async def test_update_comment_deleted_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update comment in case comment is deleted."""

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af90e6aba47cfb60efb34/",
            json={"body": "edited seventh product message"},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Comment")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_update_comment_user_updates_comment_of_another_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test update comment in case user tries to update comment of another user.
        """

        response = await test_client.patch(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af91a6aba47cfb60efb36/",
            json={},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="comment")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_comment_client_user_deletes_own_comment(
        self, test_client: AsyncClient, arrange_db: None, datetime_now_mock: MagicMock
    ) -> None:
        """Test delete comment in case client user deletes own comment."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify if comment body and status were changed
        response = await test_client.get(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "666af9246aba47cfb60efb37",
            "body": "[Deleted]",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "user_id": "65844f12b6de26578d98c2c8",
            "parent_comment_id": "666af91a6aba47cfb60efb36",
            "path": "/666af91a6aba47cfb60efb36/666af9246aba47cfb60efb37",
            "upvotes": 0,
            "downvotes": 0,
            "deleted": True,
            "created_at": "2024-06-13T13:50:28.453000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_comment_shop_side_user_deletes_own_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete comment in case shop side user deletes own comment."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9786aba47cfb60efb39/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_comment_client_user_deletes_another_clients_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete comment in case client user deletes another client's comment."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9696aba47cfb60efb38/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="comment")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_comment_shop_side_user_deletes_clients_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete comment in case shop side user deletes client's comment."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_comment_client_user_deletes_shop_side_users_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete comment in case client user deletes shop side user's comment."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9786aba47cfb60efb39/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="comment")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=SHOP_SIDE_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_delete_comment_shop_side_user_deletes_another_shop_side_user_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test delete comment in case shop side user deletes another shop side
        user's comment.
        """

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666afa3f6aba47cfb60efb3b/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_comment_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete comment in case there is no token."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_delete_comment_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete comment in case user does not have appropriate scope."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS,)],
        indirect=True,
    )
    async def test_delete_comment_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete comment in case comment is not found."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Comment")
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [(MongoCollectionsEnum.USERS, MongoCollectionsEnum.COMMENTS)],
        indirect=True,
    )
    async def test_delete_comment_deleted_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test delete comment in case comment is deleted."""

        response = await test_client.delete(
            f"{SETTINGS.APP_API_V1_PREFIX}/comments/666af90e6aba47cfb60efb34/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Comment")
        }
