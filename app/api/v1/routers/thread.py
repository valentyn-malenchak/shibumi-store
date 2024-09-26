"""Module that contains thread domain routers."""

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.auth import (
    OptionalAuthorizationDependency,
    StrictAuthorizationDependency,
)
from app.api.v1.dependencies.thread import ThreadByIdGetDependency
from app.api.v1.models.thread import (
    Thread,
    ThreadData,
)
from app.api.v1.services.thread import ThreadService

router = APIRouter(prefix="/threads", tags=["threads"])


@router.get(
    "/{thread_id}/",
    response_model=Thread,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(
            OptionalAuthorizationDependency(),
            scopes=[ScopesEnum.THREADS_GET_THREAD.name],
        )
    ],
)
async def get_thread(thread: Thread = Depends(ThreadByIdGetDependency())) -> Thread:
    """API which returns a specific thread.

    Args:
        thread (Thread): Thread object.

    Returns:
        Thread: Thread object.

    """
    return thread


@router.post(
    "/",
    response_model=Thread,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Security(
            StrictAuthorizationDependency(),
            scopes=[ScopesEnum.THREADS_CREATE_THREAD.name],
        )
    ],
)
async def create_comment(
    thread_data: ThreadData,
    thread_service: ThreadService = Depends(),
) -> Thread:
    """API which creates thread.

    Args:
        thread_data (ThreadData): Thread data.
        thread_service (ThreadService): Thread service.

    Returns:
        Thread: Thread object.

    """
    return await thread_service.create(data=thread_data)


@router.patch(
    "/{thread_id}/",
    response_model=Thread,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(
            StrictAuthorizationDependency(),
            scopes=[ScopesEnum.THREADS_UPDATE_THREAD.name],
        )
    ],
)
async def update_thread(
    thread_data: ThreadData,
    thread: Thread = Depends(ThreadByIdGetDependency()),
    thread_service: ThreadService = Depends(),
) -> Thread:
    """API which updates thread.

    Args:
        thread_data (ThreadData): Thread data.
        thread (Thread): Thread object.
        thread_service (ThreadService): Thread service.

    Returns:
        Thread: Thread object.

    """
    return await thread_service.update_by_id(id_=thread.id, data=thread_data)
