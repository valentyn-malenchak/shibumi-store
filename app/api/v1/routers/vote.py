"""Module that contains vote domain routers."""

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.api.v1.auth.auth import StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.vote import (
    VoteAccessDependency,
    VoteDataCreateDependency,
    VoteDataUpdateDependency,
)
from app.api.v1.models.vote import (
    Vote,
    VoteCreateData,
    VoteData,
)
from app.api.v1.services.vote import VoteService
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityDuplicateKeyError

router = APIRouter(prefix="/votes", tags=["votes"])


@router.get(
    "/{vote_id}/",
    response_model=Vote,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(StrictAuthorization(), scopes=[ScopesEnum.VOTES_GET_VOTE.name])
    ],
)
async def get_vote(vote: Vote = Depends(VoteAccessDependency())) -> Vote:
    """API which returns vote.

    Args:
        vote (Vote): Vote object.

    Returns:
        Vote: Vote object.

    """
    return vote


@router.post(
    "/",
    response_model=Vote,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Security(StrictAuthorization(), scopes=[ScopesEnum.VOTES_CREATE_VOTE.name])
    ],
)
async def create_vote(
    vote_data: VoteCreateData = Depends(VoteDataCreateDependency()),
    vote_service: VoteService = Depends(),
) -> Vote:
    """API which creates vote.

    Args:
        vote_data (VoteCreateData): Vote create data.
        vote_service (VoteService): Vote service.

    Returns:
        Vote: Vote object.

    Raises:
        HTTPException: in case vote is already exists for chosen comment.

    """
    try:
        return await vote_service.create(data=vote_data)

    except EntityDuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=HTTPErrorMessagesEnum.ENTITY_FIELD_UNIQUENESS.format(
                entity="Vote", field="comment_id"
            ),
        )


@router.patch(
    "/{vote_id}/",
    response_model=Vote,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(StrictAuthorization(), scopes=[ScopesEnum.VOTES_UPDATE_VOTE.name])
    ],
)
async def update_vote(
    vote_data: VoteData = Depends(VoteDataUpdateDependency()),
    vote: Vote = Depends(VoteAccessDependency()),
    vote_service: VoteService = Depends(),
) -> Vote:
    """API which updates vote.

    Args:
        vote_data (VoteData): Vote update data.
        vote (Vote): Vote object.
        vote_service (VoteService): Vote service.

    Returns:
        Vote: Vote object.

    """
    return await vote_service.update_by_id(id_=vote.id, data=vote_data)


@router.delete(
    "/{vote_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(StrictAuthorization(), scopes=[ScopesEnum.VOTES_DELETE_VOTE.name])
    ],
)
async def delete_vote(
    vote: Vote = Depends(VoteAccessDependency()),
    vote_service: VoteService = Depends(),
) -> None:
    """API which deletes vote.

    Args:
        vote (Vote): Vote object.
        vote_service (VoteService): Vote service.

    """
    return await vote_service.delete(item=vote)
