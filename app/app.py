"""Main module for running the FastAPI application."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import routers


class App:
    """Main application class for running the FastAPI app."""

    def __init__(self):
        """Initialize the App class."""
        self.api = FastAPI()

        # configure application routes
        self.configure_routes()

        # configure application middlewares
        self.configure_middlewares()

    def configure_routes(self):
        """Configure the routes for the FastAPI app."""
        for router_ in routers:
            self.api.include_router(router_)

    def configure_middlewares(self):
        """Configure the middlewares for the FastAPI app."""
        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=[],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["Authorization"],
        )

    def run(self):
        """Run the FastAPI app."""
        uvicorn.run(self.api, host="0.0.0.0", port=8000)


app = App()

if __name__ == "__main__":
    app.run()
