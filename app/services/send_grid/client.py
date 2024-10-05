"""Contains SendGrid client."""

from sendgrid import SendGridAPIClient  # type: ignore

from app.services.base import BaseClient
from app.settings import SETTINGS


class SendGridClient(BaseClient):
    """SendGrid client."""

    _client = SendGridAPIClient(api_key=SETTINGS.SEND_GRID_API_KEY)

    @property
    def client(self) -> SendGridAPIClient:
        """SendGrid client getter."""
        return self._client

    @classmethod
    async def close(cls) -> None:
        """Closes client."""
