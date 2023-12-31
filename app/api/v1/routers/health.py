"""Module that contains health domain router."""

from typing import Dict

from fastapi import APIRouter, status

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=dict, status_code=status.HTTP_200_OK)
async def health() -> Dict[str, str]:
    """API which checks the health of the application."""
    return {"status": "healthy"}
