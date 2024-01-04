"""Module that contains health domain router."""

from typing import Dict

from fastapi import APIRouter, Security, status

from app.api.v1.auth.auth import StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.users import User

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=dict, status_code=status.HTTP_200_OK)
async def health(
    _: User = Security(
        StrictAuthorization(), scopes=[ScopesEnum.HEALTH_GET_HEALTH.name]
    ),
) -> Dict[str, str]:
    """API which checks the health of the application."""
    return {"status": "healthy"}
