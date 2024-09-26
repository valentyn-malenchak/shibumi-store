"""Module that contains health domain router."""

from fastapi import APIRouter, Security, status

from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.auth import StrictAuthorizationDependency

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(
            StrictAuthorizationDependency(), scopes=[ScopesEnum.HEALTH_GET_HEALTH.name]
        )
    ],
)
async def get_health() -> dict[str, str]:
    """API which checks the health of the application."""
    return {"status": "healthy"}
