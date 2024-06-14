"""Module that contains thread domain routers."""

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.comment import (
    CommentByIdDependency,
    CommentDataCreateDependency,
)
from app.api.v1.dependencies.thread import ThreadByIdDependency
from app.api.v1.models.thread import Comment, CommentCreateData, Thread
from app.api.v1.models.user import CurrentUser
from app.api.v1.services.comment import CommentService

router = APIRouter(prefix="/threads", tags=["threads"])


@router.get(
    "/{thread_id}/",
    response_model=Thread,
    status_code=status.HTTP_200_OK,
)
async def get_thread(
    _: CurrentUser | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.THREADS_GET_THREAD.name]
    ),
    thread: Thread = Depends(ThreadByIdDependency()),
) -> Thread:
    """API which returns a specific thread.

    Args:
        _ (CurrentUser | None): Current user object or None.
        thread (Thread): Thread object.

    Returns:
        Thread: Thread object.

    """
    return thread


@router.get(
    "/{thread_id}/comments/{comment_id}/",
    response_model=Comment,
    status_code=status.HTTP_200_OK,
)
async def get_thread_comment(
    _: CurrentUser | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.THREADS_GET_COMMENT.name]
    ),
    comment: Comment = Depends(CommentByIdDependency()),
) -> Comment:
    """API which returns thread comment.

    Args:
        _ (CurrentUser | None): Current user object or None.
        comment (Comment): Comment object.

    Returns:
        Comment: Comment object.

    """
    return comment


@router.post(
    "/{thread_id}/comments/",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
)
async def create_thread_comment(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.THREADS_CREATE_MESSAGE.name]
    ),
    comment_data: CommentCreateData = Depends(CommentDataCreateDependency()),
    comment_service: CommentService = Depends(),
) -> Comment:
    """API which creates thread comment.

    Args:
        _ (CurrentUser): Current user object.
        comment_data (CommentCreateData): Comment create data.
        comment_service (CommentService): Comment service.

    Returns:
        Comment: Comment object.

    """
    return await comment_service.create(data=comment_data)
