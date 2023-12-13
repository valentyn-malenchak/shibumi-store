"""Main module for running the FastAPI application."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import ROUTERS
from app.services import SERVICES
from app.settings import SETTINGS


class App:
    """Main application class for running the FastAPI app."""

    def __init__(self) -> None:
        """Initialize the App class."""
        self.api = FastAPI()

        # configure application routes
        self._configure_routes()

        # configure application middlewares
        self._configure_middlewares()

        # configure application handlers
        self._configure_handlers()

        # load application configuration
        self._load_app_config()

    def _configure_routes(self) -> None:
        """Configure the routes for the FastAPI app."""
        for router_ in ROUTERS:
            self.api.include_router(router_)

    def _configure_middlewares(self) -> None:
        """Configure the middlewares for the FastAPI app."""
        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=[],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["Authorization"],
        )

    def _configure_handlers(self) -> None:
        """Configure the handlers for the FastAPI app."""
        self.api.add_event_handler("startup", self._startup_services)
        self.api.add_event_handler("shutdown", self._shutdown_services)

    @staticmethod
    def _startup_services() -> None:
        """Startup external services."""
        for service in SERVICES:
            service.on_startup()

    @staticmethod
    def _shutdown_services() -> None:
        """Shutdown external services."""
        for service in SERVICES:
            service.on_shutdown()

    def _load_app_config(self) -> None:
        """Loads application level configuration."""
        # store config into FastApi
        self.api.state.config = SETTINGS

    def run(self) -> None:
        """Run the FastAPI app."""
        uvicorn.run(self.api, host="0.0.0.0", port=8000, reload=SETTINGS.DEBUG)


app = App()

if __name__ == "__main__":
    app.run()
