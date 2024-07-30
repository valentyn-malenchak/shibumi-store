"""Module that contains tests for comments routes."""

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


class TestComment(BaseAPITest):
    """Test class for comment APIs endpoints in the FastAPI application."""

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
    async def test_get_thread_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
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
            "created_at": "2024-06-13T13:50:28.453000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
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
    async def test_get_thread_comment_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment in case there is no token."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
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
            "created_at": "2024-06-13T13:50:28.453000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_thread_comment_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment in case user does not have appropriate scope."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_thread_comment_thread_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment in case thread is not found."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
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
    async def test_get_thread_comment_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment in case comment is not found."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
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
    async def test_get_thread_comment_comment_is_not_related_to_thread(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment in case comment does not belong to thread."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5de4cef83e11dbc7ac2/comments/666af9246aba47cfb60efb37/",
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
                MongoCollectionsEnum.THREADS,
            )
        ],
        indirect=True,
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_create_thread_comment_root_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment in case of root comment."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/",
            json={"body": "some product question 1", "parent_comment_id": None},
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
    @freeze_time(FROZEN_DATETIME)
    async def test_create_thread_comment_with_parent(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment in case comment has parent."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/",
            json={
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
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_thread_comment_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment in case there is no token."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/",
            json={"body": "some product question 1", "parent_comment_id": None},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_thread_comment_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment in case user does not have appropriate scope."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/",
            json={"body": "some product question 1", "parent_comment_id": None},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_thread_comment_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment in case request data is invalid."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/",
            json={"parent_comment_id": 123},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "body"], "Field required"),
            ("object_id", ["body", "parent_comment_id"], "Invalid object identifier."),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_thread_comment_thread_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment in case thread is not found."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/",
            json={"body": "some product question 1", "parent_comment_id": None},
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
    async def test_create_thread_comment_parent_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment in case parent comment is not found."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/",
            json={
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
    async def test_create_thread_comment_parent_comment_is_not_related_to_thread(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test create thread comment in case parent comment does not belong to thread.
        """

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5de4cef83e11dbc7ac2/comments/",
            json={
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
                MongoCollectionsEnum.THREADS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_update_thread_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
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
            "created_at": "2024-06-13T13:50:28.453000",
            "updated_at": FROZEN_DATETIME,
        }

    @pytest.mark.asyncio
    async def test_update_thread_comment_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment in case there is no token."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
            json={"body": "edited seventh product message"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_thread_comment_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment in case user does not have appropriate scope."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
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
                MongoCollectionsEnum.THREADS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_update_thread_comment_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment in case request data is invalid."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
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
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_thread_comment_thread_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment in case thread is not found."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
            json={},
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
    async def test_update_thread_comment_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment in case comment is not found."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/",
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
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.THREADS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_update_thread_comment_comment_is_not_related_to_thread(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test update thread comment in case comment does not belong to thread.
        """

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5de4cef83e11dbc7ac2/comments/666af9246aba47cfb60efb37/",
            json={},
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
                MongoCollectionsEnum.THREADS,
                MongoCollectionsEnum.COMMENTS,
            )
        ],
        indirect=True,
    )
    async def test_update_thread_comment_user_updates_comment_of_another_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test update thread comment in case user tries to update comment of another user.
        """

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af91a6aba47cfb60efb36/",
            json={},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.COMMENT_ACCESS_DENIED
        }
