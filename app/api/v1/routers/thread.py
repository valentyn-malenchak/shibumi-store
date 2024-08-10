"""Module that contains thread domain routers."""

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.thread import (
    ThreadByIdDependency,
    ThreadDataDependency,
)
from app.api.v1.models.thread import (
    Thread,
    ThreadData,
)
from app.api.v1.models.user import CurrentUser
from app.api.v1.services.thread import ThreadService

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


@router.post(
    "/",
    response_model=Thread,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.THREADS_CREATE_THREAD.name]
    ),
    thread_data: ThreadData = Depends(ThreadDataDependency()),
    thread_service: ThreadService = Depends(),
) -> Thread:
    """API which creates thread.

    Args:
        _ (CurrentUser): Current user object.
        thread_data (ThreadData): Thread create data.
        thread_service (ThreadService): Thread service.

    Returns:
        Thread: Thread object.

    """
    return await thread_service.create(data=thread_data)


@router.patch(
    "/{thread_id}/",
    response_model=Thread,
    status_code=status.HTTP_200_OK,
)
async def update_thread(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.THREADS_UPDATE_THREAD.name]
    ),
    thread_data: ThreadData = Depends(ThreadDataDependency()),
    thread: Thread = Depends(ThreadByIdDependency()),
    thread_service: ThreadService = Depends(),
) -> Thread:
    """API which updates thread.

    Args:
        _ (CurrentUser): Current user object.
        thread_data (ThreadData): Thread data.
        thread (Thread): Thread object.
        thread_service (ThreadService): Thread service.

    Returns:
        Thread: Thread object.

    """
    return await thread_service.update_by_id(id_=thread.id, data=thread_data)
