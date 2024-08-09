"""Module that contains vote domain routers."""

from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.vote import (
    VoteDataCreateDependency,
    VoteDataUpdateDependency,
    VoteUserDependency,
)
from app.api.v1.models.user import CurrentUser
from app.api.v1.models.vote import (
    Vote,
    VoteCreateData,
    VoteData,
)
from app.api.v1.services.vote import VoteService
from app.utils.pydantic import ObjectIdAnnotation

router = APIRouter(prefix="/votes", tags=["votes"])


@router.get(
    "/{vote_id}/",
    response_model=Vote,
    status_code=status.HTTP_200_OK,
)
async def get_vote(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.VOTES_GET_VOTE.name]
    ),
    vote: Vote = Depends(VoteUserDependency()),
) -> Vote:
    """API which returns vote.

    Args:
        _ (CurrentUser): Current user object.
        vote (Vote): Vote object.

    Returns:
        Vote: Vote object.

    """
    return vote


@router.post(
    "/",
    response_model=Vote,
    status_code=status.HTTP_201_CREATED,
)
async def create_vote(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.VOTES_CREATE_VOTE.name]
    ),
    vote_data: VoteCreateData = Depends(VoteDataCreateDependency()),
    vote_service: VoteService = Depends(),
) -> Vote:
    """API which creates vote.

    Args:
        _ (CurrentUser): Current user object.
        vote_data (VoteCreateData): Vote create data.
        vote_service (VoteService): Vote service.

    Returns:
        Vote: Vote object.

    """
    return await vote_service.create(data=vote_data)


@router.patch(
    "/{vote_id}/",
    response_model=Vote,
    status_code=status.HTTP_200_OK,
)
async def update_vote(
    vote_id: Annotated[ObjectId, ObjectIdAnnotation],
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.VOTES_UPDATE_VOTE.name]
    ),
    vote_data: VoteData = Depends(VoteDataUpdateDependency()),
    vote_service: VoteService = Depends(),
) -> Vote:
    """API which updates vote.

    Args:
        vote_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
        identifier of requested vote.
        _ (CurrentUser): Current user object.
        vote_data (VoteData): Vote update data.
        vote_service (VoteService): Vote service.

    Returns:
        Vote: Vote object.

    """
    return await vote_service.update_by_id(id_=vote_id, data=vote_data)


@router.delete(
    "/{vote_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_vote(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.VOTES_DELETE_VOTE.name]
    ),
    vote: Vote = Depends(VoteUserDependency()),
    vote_service: VoteService = Depends(),
) -> None:
    """API which deletes vote.

    Args:
        _ (CurrentUser): Current user object.
        vote (Vote): Vote object.
        vote_service (VoteService): Vote service.

    """
    return await vote_service.delete(item=vote)
