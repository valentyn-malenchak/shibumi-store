"""Module that contains comment domain routers."""

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.comment import (
    CommentByIdGetDependency,
    CommentDataCreateDependency,
    CommentDeleteAccessDependency,
    CommentUpdateAccessDependency,
)
from app.api.v1.models.comment import (
    Comment,
    CommentCreateData,
    CommentUpdateData,
)
from app.api.v1.services.comment import CommentService

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get(
    "/{comment_id}/",
    response_model=Comment,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(OptionalAuthorization(), scopes=[ScopesEnum.COMMENTS_GET_COMMENT.name])
    ],
)
async def get_comment(
    comment: Comment = Depends(CommentByIdGetDependency()),
) -> Comment:
    """API which returns comment.

    Args:
        comment (Comment): Comment object.

    Returns:
        Comment: Comment object.

    """
    return comment


@router.post(
    "/",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Security(
            StrictAuthorization(), scopes=[ScopesEnum.COMMENTS_CREATE_COMMENT.name]
        ),
    ],
)
async def create_comment(
    comment_data: CommentCreateData = Depends(CommentDataCreateDependency()),
    comment_service: CommentService = Depends(),
) -> Comment:
    """API which creates comment.

    Args:
        comment_data (CommentCreateData): Comment create data.
        comment_service (CommentService): Comment service.

    Returns:
        Comment: Comment object.

    """
    return await comment_service.create(data=comment_data)


@router.patch(
    "/{comment_id}/",
    response_model=Comment,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(
            StrictAuthorization(), scopes=[ScopesEnum.COMMENTS_UPDATE_COMMENT.name]
        )
    ],
)
async def update_comment(
    comment_data: CommentUpdateData,
    comment: Comment = Depends(CommentUpdateAccessDependency()),
    comment_service: CommentService = Depends(),
) -> Comment:
    """API which updates comment.

    Args:
        comment_data (CommentUpdateData): Comment update data.
        comment (CommentCreateData): Comment object.
        comment_service (CommentService): Comment service.

    Returns:
        Comment: Comment object.

    """
    return await comment_service.update_by_id(id_=comment.id, data=comment_data)


@router.delete(
    "/{comment_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(
            StrictAuthorization(), scopes=[ScopesEnum.COMMENTS_DELETE_COMMENT.name]
        )
    ],
)
async def delete_comment(
    comment: Comment = Depends(CommentDeleteAccessDependency()),
    comment_service: CommentService = Depends(),
) -> None:
    """API which softly deletes comment.

    Args:
        comment (CommentCreateData): Comment object.
        comment_service (CommentService): Comment service.

    """
    return await comment_service.delete_by_id(id_=comment.id)
