"""Module that collects all routers."""

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.user import router as user_router

ROUTERS = [
    health_router,
    auth_router,
    user_router,
]
