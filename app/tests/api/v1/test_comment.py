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
            "author_id": "65844f12b6de26578d98c2c8",
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
            "author_id": "65844f12b6de26578d98c2c8",
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
