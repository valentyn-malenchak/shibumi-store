"""Contains background tasks."""

import abc
from typing import Any

from fastapi import BackgroundTasks, Depends

from app.services.send_grid.service import SendGridService


class BaseTask(abc.ABC):
    """Base background task."""

    def __init__(self, background_tasks: BackgroundTasks) -> None:
        """Initialize base background task.

        Args:
            background_tasks (BackgroundTasks): Background tasks.

        """
        self.background_tasks = background_tasks

    @abc.abstractmethod
    async def __call__(self, *args: Any) -> Any:
        """Executes the task.

        Args:
            args (Any): Task arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class SendEmailTask(BaseTask):
    """Send email background task."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        send_grid_service: SendGridService = Depends(),
    ) -> None:
        """Initialize send email task.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            send_grid_service (SendGridService): SendGrid service.

        """

        super().__init__(background_tasks=background_tasks)

        self.send_grid_service = send_grid_service

    async def __call__(
        self, to_emails: str, subject: str, plain_text_content: str
    ) -> None:
        """Sends an email using SendGrid.

        Args:
            to_emails (str): Email of receiver.
            subject (str): Email subject.
            plain_text_content (str): Email text.

        """

        self.background_tasks.add_task(
            self.send_grid_service.send,
            to_emails=to_emails,
            subject=subject,
            plain_text_content=plain_text_content,
        )
