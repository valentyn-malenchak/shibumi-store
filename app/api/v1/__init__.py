"""Module that collects all routers."""

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.users import router as users_router

ROUTERS = [
    health_router,
    auth_router,
    users_router,
]
