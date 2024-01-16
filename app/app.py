"""Main module for running the FastAPI application."""

from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import ROUTERS
from app.services import SERVICE_CLIENTS
from app.settings import SETTINGS


class App(FastAPI):
    """Main application class for running the FastAPI app."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the App class."""

        super().__init__(**kwargs)

        # configure application routes
        self._configure_routes()

        # configure application middlewares
        self._configure_middlewares()

        # configure application handlers
        self._configure_handlers()

        # load application configuration into FastApi
        self.state.config = SETTINGS

    def _configure_routes(self) -> None:
        """Configure the routes for the FastAPI app."""
        for router_ in ROUTERS:
            self.include_router(router_)

    def _configure_middlewares(self) -> None:
        """Configure the middlewares for the FastAPI app."""
        self.add_middleware(
            CORSMiddleware,
            allow_origins=[],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["Authorization"],
        )

    def _configure_handlers(self) -> None:
        """Configure the handlers for the FastAPI app."""
        self.add_event_handler("shutdown", self._shutdown)

    @staticmethod
    async def _shutdown() -> None:
        """Executes on application shutdown."""
        # close clients of external services
        for client in SERVICE_CLIENTS:
            client.close()

    def run(self) -> None:
        """Run the FastAPI app."""
        uvicorn.run(
            "__main__:app",
            host="0.0.0.0",
            port=8000,
            reload=self.state.config.APP_DEBUG,
            workers=self.state.config.APP_WORKERS,
        )


app = App()

if __name__ == "__main__":
    app.run()
