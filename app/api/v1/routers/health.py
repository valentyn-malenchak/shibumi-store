"""Module that contains health domain router."""

from fastapi import APIRouter, Security, status

from app.api.v1.auth.auth import StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.user import CurrentUserModel

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=dict, status_code=status.HTTP_200_OK)
async def get_health(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.HEALTH_GET_HEALTH.name]
    ),
) -> dict[str, str]:
    """API which checks the health of the application."""
    return {"status": "healthy"}
