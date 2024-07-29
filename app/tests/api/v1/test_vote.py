"""Module that contains tests for votes routes."""

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


class TestVote(BaseAPITest):
    """Test class for vote APIs endpoints in the FastAPI application."""

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.THREADS,
                MongoCollectionsEnum.COMMENTS,
                MongoCollectionsEnum.VOTES,
            )
        ],
        indirect=True,
    )
    async def test_get_thread_comment_vote(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment vote."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "6692aa64c8c252998d87ad2b",
            "user_id": "65844f12b6de26578d98c2c8",
            "comment_id": "666af8ae6aba47cfb60efb31",
            "value": True,
            "created_at": "2024-07-13T13:48:30.209000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_get_thread_comment_vote_no_token(
        self, test_client: AsyncClient
    ) -> None:
        """Test get thread comment vote in case there is no token."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_thread_comment_vote_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment vote in case user does not have appropriate scope."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_get_thread_comment_vote_thread_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment vote in case thread is not found."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
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
    async def test_get_thread_comment_vote_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment vote in case comment is not found."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/votes/6692aa64c8c252998d87ad2b/",
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
    async def test_get_thread_comment_vote_comment_is_not_related_to_thread(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment vote in case comment does not belong to thread."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5de4cef83e11dbc7ac2/comments/666af9246aba47cfb60efb37/votes/6692aa64c8c252998d87ad2b/",
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
    async def test_get_thread_comment_vote_vote_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment vote in case vote is not found."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/votes/6692aa64c8c252998d87ad2b/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Vote")
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
                MongoCollectionsEnum.VOTES,
            )
        ],
        indirect=True,
    )
    async def test_get_thread_comment_vote_vote_is_not_related_to_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test get thread comment vote in case vote does not belong to comment."""

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/6692aa64c8c252998d87ad2b/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITIES_ARE_NOT_RELATED.format(
                child_entity="Vote", parent_entity="comment"
            )
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
                MongoCollectionsEnum.VOTES,
            )
        ],
        indirect=True,
    )
    async def test_get_thread_comment_vote_user_gets_vote_of_another_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test get thread comment vote in case user tries to get vote of another user.
        """

        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/66a7f2196da2a20f1db87a29/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.VOTE_ACCESS_DENIED}

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
    async def test_create_thread_comment_vote_positive(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment vote in case of upvote."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/",
            json={"value": True},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert self._exclude_fields(response.json(), exclude_keys=["id"]) == {
            "value": True,
            "comment_id": "666af8c16aba47cfb60efb32",
            "user_id": "65844f12b6de26578d98c2c8",
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

        # Checks if upvote counter changes
        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.json() == {
            "id": "666af8c16aba47cfb60efb32",
            "body": "second product message",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "author_id": "65844f12b6de26578d98c2c8",
            "parent_comment_id": None,
            "path": "/666af8c16aba47cfb60efb32",
            "upvotes": 1,
            "downvotes": 0,
            "created_at": "2024-06-13T13:48:49.788000",
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
    async def test_create_thread_comment_vote_negative(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment vote in case of downvote."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/",
            json={"value": False},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert self._exclude_fields(response.json(), exclude_keys=["id"]) == {
            "value": False,
            "comment_id": "666af8c16aba47cfb60efb32",
            "user_id": "65844f12b6de26578d98c2c8",
            "created_at": FROZEN_DATETIME,
            "updated_at": None,
        }

        # Checks if downvote counter changes
        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/",
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.json() == {
            "id": "666af8c16aba47cfb60efb32",
            "body": "second product message",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "author_id": "65844f12b6de26578d98c2c8",
            "parent_comment_id": None,
            "path": "/666af8c16aba47cfb60efb32",
            "upvotes": 0,
            "downvotes": 1,
            "created_at": "2024-06-13T13:48:49.788000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_create_thread_comment_vote_no_token(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment vote in case there is no token."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/",
            json={"value": True},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_thread_comment_vote_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test create thread comment vote in case user does not have appropriate scope.
        """

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/",
            json={"value": True},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_thread_comment_vote_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment vote in case request data is invalid."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/",
            json={},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "value"], "Field required"),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_create_thread_comment_vote_thread_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment vote in case thread is not found."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/",
            json={"value": True},
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
    async def test_create_thread_comment_vote_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test create thread comment vote in case comment is not found."""

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/",
            json={"value": True},
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
    async def test_create_thread_comment_vote_comment_is_not_related_to_thread(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test create thread comment vote in case comment does not belong to thread.
        """

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5de4cef83e11dbc7ac2/comments/666af9246aba47cfb60efb37/votes/",
            json={"value": True},
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
                MongoCollectionsEnum.VOTES,
            )
        ],
        indirect=True,
    )
    async def test_create_thread_comment_vote_user_comment_vote_is_already_created(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test create thread comment vote in case user vote for comment is already
        created.
        """

        response = await test_client.post(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/",
            json={"value": True},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_FIELD_UNIQUENESS.format(
                entity="Vote",
                field="comment_id",
            )
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
                MongoCollectionsEnum.VOTES,
            )
        ],
        indirect=True,
    )
    @freeze_time(FROZEN_DATETIME)
    async def test_update_thread_comment_vote(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment vote."""

        # Change to downvote
        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            json={"value": False},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "6692aa64c8c252998d87ad2b",
            "user_id": "65844f12b6de26578d98c2c8",
            "comment_id": "666af8ae6aba47cfb60efb31",
            "value": False,
            "created_at": "2024-07-13T13:48:30.209000",
            "updated_at": FROZEN_DATETIME,
        }

        # Check if count of upvotes/downvotes changed
        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "666af8ae6aba47cfb60efb31",
            "body": "first product message",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "author_id": "6597f14332e631f7fed1a114",
            "parent_comment_id": None,
            "path": "/666af8ae6aba47cfb60efb31",
            "upvotes": 0,
            "downvotes": 2,
            "created_at": "2024-06-13T13:48:30.209000",
            "updated_at": None,
        }

        # Change to upvote
        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            json={"value": True},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "6692aa64c8c252998d87ad2b",
            "user_id": "65844f12b6de26578d98c2c8",
            "comment_id": "666af8ae6aba47cfb60efb31",
            "value": True,
            "created_at": "2024-07-13T13:48:30.209000",
            "updated_at": FROZEN_DATETIME,
        }

        # Check if count of upvotes/downvotes changed
        response = await test_client.get(
            f"{AppConstants.API_V1_PREFIX}/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": "666af8ae6aba47cfb60efb31",
            "body": "first product message",
            "thread_id": "6669b5634cef83e11dbc7abf",
            "author_id": "6597f14332e631f7fed1a114",
            "parent_comment_id": None,
            "path": "/666af8ae6aba47cfb60efb31",
            "upvotes": 1,
            "downvotes": 1,
            "created_at": "2024-06-13T13:48:30.209000",
            "updated_at": None,
        }

    @pytest.mark.asyncio
    async def test_update_thread_comment_vote_no_token(
        self, test_client: AsyncClient
    ) -> None:
        """Test update thread comment vote in case there is no token."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            json={"value": False},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": HTTPErrorMessagesEnum.NOT_AUTHORIZED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=USER_NO_SCOPES))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_thread_comment_vote_no_scope(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test update thread comment vote in case user does not have appropriate scope.
        """

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            json={"value": False},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.PERMISSION_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_thread_comment_vote_validate_data(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment vote in case request data is invalid."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            json={},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert [
            (error["type"], error["loc"], error["msg"])
            for error in response.json()["detail"]
        ] == [
            ("missing", ["body", "value"], "Field required"),
        ]

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db", [(MongoCollectionsEnum.USERS,)], indirect=True
    )
    async def test_update_thread_comment_vote_thread_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment vote in case thread is not found."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            json={"value": False},
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
    async def test_update_thread_comment_vote_comment_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment vote in case comment is not found."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/votes/6692aa64c8c252998d87ad2b/",
            json={"value": False},
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
    async def test_update_thread_comment_vote_comment_is_not_related_to_thread(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment vote in case comment does not belong to thread."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5de4cef83e11dbc7ac2/comments/666af9246aba47cfb60efb37/votes/6692aa64c8c252998d87ad2b/",
            json={"value": False},
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
    async def test_update_thread_comment_vote_vote_is_not_found(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment vote in case vote is not found."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af9246aba47cfb60efb37/votes/6692aa64c8c252998d87ad2b/",
            json={"value": False},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Vote")
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
                MongoCollectionsEnum.VOTES,
            )
        ],
        indirect=True,
    )
    async def test_update_thread_comment_vote_vote_is_not_related_to_comment(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """Test update thread comment vote in case vote does not belong to comment."""

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8c16aba47cfb60efb32/votes/6692aa64c8c252998d87ad2b/",
            json={"value": False},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": HTTPErrorMessagesEnum.ENTITIES_ARE_NOT_RELATED.format(
                child_entity="Vote", parent_entity="comment"
            )
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
                MongoCollectionsEnum.VOTES,
            )
        ],
        indirect=True,
    )
    async def test_update_thread_comment_vote_user_updates_vote_of_another_user(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test update thread comment vote in case user tries to update vote
        of another user.
        """

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/66a7f2196da2a20f1db87a29/",
            json={"value": False},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": HTTPErrorMessagesEnum.VOTE_ACCESS_DENIED}

    @pytest.mark.asyncio
    @patch("jwt.decode", Mock(return_value=CUSTOMER_USER))
    @pytest.mark.parametrize(
        "arrange_db",
        [
            (
                MongoCollectionsEnum.USERS,
                MongoCollectionsEnum.THREADS,
                MongoCollectionsEnum.COMMENTS,
                MongoCollectionsEnum.VOTES,
            )
        ],
        indirect=True,
    )
    async def test_update_thread_comment_vote_same_value(
        self, test_client: AsyncClient, arrange_db: None
    ) -> None:
        """
        Test update thread comment vote in case user tries to set the same value.
        """

        response = await test_client.patch(
            f"{AppConstants.API_V1_PREFIX}"
            f"/threads/6669b5634cef83e11dbc7abf/comments/666af8ae6aba47cfb60efb31/votes/6692aa64c8c252998d87ad2b/",
            json={"value": True},
            headers={"Authorization": f"Bearer {TEST_JWT}"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {"detail": HTTPErrorMessagesEnum.INVALID_VOTE_VALUE}
