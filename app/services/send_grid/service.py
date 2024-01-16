"""Module that contains SendGrid service."""

import logging

from fastapi import Depends
from sendgrid.helpers.mail import Mail  # type: ignore
from tenacity import retry, stop_after_attempt, wait_fixed

from app.constants import BACKGROUND_TASK_RETRY, BACKGROUND_TASK_RETRY_WAIT
from app.services.base import BaseService
from app.services.send_grid.client import SendGridClient
from app.settings import SETTINGS


class SendGridService(BaseService):
    """SendGrid service facade."""

    _name: str = "send_grid"

    def __init__(self, send_grid_client: SendGridClient = Depends()) -> None:
        """Redis service initialization method.

        Args:
            send_grid_client (SendGridClient): SendGrid client.

        """

        self._client = send_grid_client.client

    @retry(
        stop=stop_after_attempt(BACKGROUND_TASK_RETRY),
        wait=wait_fixed(BACKGROUND_TASK_RETRY_WAIT),
    )
    def send(self, to_emails: str, subject: str, plain_text_content: str) -> None:
        """Sends an email using SendGrid.

        Args:
            to_emails (str): Email of receiver.
            subject (str): Email subject.
            plain_text_content (str): Email text.

        """

        mail = Mail(
            from_email=SETTINGS.SEND_GRID_SENDER_EMAIL,
            to_emails=to_emails,
            subject=subject,
            plain_text_content=plain_text_content,
        )

        try:
            self._client.send(mail)

        except Exception as e:
            logging.error(f"Error sending email to '{to_emails}': {e}")
            raise e
