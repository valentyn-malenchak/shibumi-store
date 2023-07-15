"""Module that contains health router."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=dict)
def health():
    """Health endpoint to check the status of the application."""
    return {"status": "healthy"}
