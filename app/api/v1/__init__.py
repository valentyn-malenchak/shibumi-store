"""Module that collects all routers."""

from app.api.v1.routers.health import router as health_router

routers = [
    health_router,
]
