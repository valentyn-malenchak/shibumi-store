"""Contains application injector."""

from injector import Injector

from app.api.v1.repositories.users import UserRepository
from app.api.v1.services.users import UserService
from app.services.mongo.service import MongoDBService


class InjectorConfigurator:
    """Injector configurator."""

    def __init__(self) -> None:
        """Initialization method for injector configurator."""

        self._injector = Injector()

        self._interfaces_to_bind = [
            UserRepository,
            UserService,
            MongoDBService,
        ]

        self.bind_interface()

    def bind_interface(self) -> None:
        """Binds application interfaces to injects."""
        for interface in self._interfaces_to_bind:
            self._injector.binder.bind(interface)

    @property
    def injector(self) -> Injector:
        return self._injector


configurator = InjectorConfigurator()
injector = configurator.injector
