"""Commands resource — OpenAPI tag Commands.

Paths: GET/POST/DELETE ``/commands/{deviceId}``.
"""

from __future__ import annotations

from typing import List

from posiverse.models import Command
from posiverse.resources._base import BaseResource


class CommandsResource(BaseResource):
    """Manage queued device commands (OpenAPI tag Commands)."""

    def list(self, device_id: str) -> List[Command]:
        """List pending commands for a device (operation ``getCommands``).

        Args:
            device_id: Device UUID.

        Returns:
            List of :class:`~posiverse.models.command.Command` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            NotFoundError: Device not found.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/commands/{device_id}")
        return [Command.model_validate(item) for item in (data or [])]

    def add(self, device_id: str, command: str) -> None:
        """Queue a command on a device (operation ``addCommand``).

        The OpenAPI request body is ``text/plain`` containing the command
        string (for example ``\"reset\"``).

        Args:
            device_id: Device UUID.
            command: Command string to execute on the device.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            NotFoundError: Device not found.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request(
            "POST",
            f"/commands/{device_id}",
            content=command,
            headers={"Content-Type": "text/plain"},
        )

    def delete(self, device_id: str) -> None:
        """Delete pending commands for a device (operation ``deleteCommand``).

        Args:
            device_id: Device UUID.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            NotFoundError: Device not found.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request("DELETE", f"/commands/{device_id}")
