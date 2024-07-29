"""Module that contains thread domain routers."""

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.comment import (
    CommentAuthorDependency,
    CommentByIdDependency,
    CommentDataCreateDependency,
    CommentDataUpdateDependency,
)
from app.api.v1.dependencies.thread import ThreadByIdDependency
from app.api.v1.dependencies.vote import (
    VoteAuthorDependency,
    VoteDataCreateDependency,
    VoteDataUpdateDependency,
)
from app.api.v1.models.thread import (
    Comment,
    CommentCreateData,
    CommentUpdateData,
    Thread,
    Vote,
    VoteCreateData,
    VoteUpdateData,
)
from app.api.v1.models.user import CurrentUser
from app.api.v1.services.comment import CommentService
from app.api.v1.services.vote import VoteService

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
        StrictAuthorization(), scopes=[ScopesEnum.THREADS_CREATE_COMMENT.name]
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


@router.patch(
    "/{thread_id}/comments/{comment_id}/",
    response_model=Comment,
    status_code=status.HTTP_200_OK,
)
async def update_thread_comment(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.THREADS_UPDATE_COMMENT.name]
    ),
    comment_data: CommentUpdateData = Depends(CommentDataUpdateDependency()),
    comment: Comment = Depends(CommentAuthorDependency()),
    comment_service: CommentService = Depends(),
) -> Comment:
    """API which updates thread comment.

    Args:
        _ (CurrentUser): Current user object.
        comment_data (CommentUpdateData): Comment update data.
        comment (CommentCreateData): Comment object.
        comment_service (CommentService): Comment service.

    Returns:
        Comment: Comment object.

    """
    return await comment_service.update_by_id(id_=comment.id, data=comment_data)


@router.get(
    "/{thread_id}/comments/{comment_id}/votes/{vote_id}/",
    response_model=Vote,
    status_code=status.HTTP_200_OK,
)
async def get_thread_comment_vote(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.THREADS_GET_VOTE.name]
    ),
    vote: Vote = Depends(VoteAuthorDependency()),
) -> Vote:
    """API which returns thread comment vote.

    Args:
        _ (CurrentUser): Current user object.
        vote (Vote): Vote object.

    Returns:
        Vote: Vote object.

    """
    return vote


@router.post(
    "/{thread_id}/comments/{comment_id}/votes/",
    response_model=Vote,
    status_code=status.HTTP_201_CREATED,
)
async def create_thread_comment_vote(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.THREADS_CREATE_VOTE.name]
    ),
    vote_data: VoteCreateData = Depends(VoteDataCreateDependency()),
    vote_service: VoteService = Depends(),
) -> Vote:
    """API which creates thread comment vote.

    Args:
        _ (CurrentUser): Current user object.
        vote_data (VoteCreateData): Vote create data.
        vote_service (VoteService): Vote service.

    Returns:
        Vote: Vote object.

    """
    return await vote_service.create(data=vote_data)


@router.patch(
    "/{thread_id}/comments/{comment_id}/votes/{vote_id}/",
    response_model=Vote,
    status_code=status.HTTP_200_OK,
)
async def update_thread_comment_vote(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.THREADS_UPDATE_VOTE.name]
    ),
    vote_data: VoteUpdateData = Depends(VoteDataUpdateDependency()),
    vote_service: VoteService = Depends(),
) -> Vote:
    """API which updates thread comment vote.

    Args:
        _ (CurrentUser): Current user object.
        vote_data (VoteUpdateData): Vote update data.
        vote_service (VoteService): Vote service.

    Returns:
        Vote: Vote object.

    """
    return await vote_service.update_by_id(id_=vote_data.vote_id, data=vote_data)
