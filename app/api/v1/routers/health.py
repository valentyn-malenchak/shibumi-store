"""Module that contains health router."""

from typing import Dict

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=dict)
def health() -> Dict[str, str]:
    """Health endpoint to check the status of the application."""
    return {"status": "healthy"}
