"""VirtualConsole resource — OpenAPI tag VirtualConsole.

Paths: GET/PUT ``/virtualconsole/{deviceId}``.
"""

from __future__ import annotations

from typing import List

from posiverse.models import ConsoleLine
from posiverse.resources._base import BaseResource


class VirtualConsoleResource(BaseResource):
    """Read console output and send commands as if using a serial port."""

    def get_output(self, device_id: str, *, last_date: int) -> List[ConsoleLine]:
        """Poll stored console output (operation ``getConsoleOutput``).

        Args:
            device_id: Device UUID.
            last_date: Timestamp of the last received line. Pass ``0`` to
                retrieve all stored console output (OpenAPI ``lastDate``).

        Returns:
            List of :class:`~posiverse.models.console.ConsoleLine` objects.

        Raises:
            NotFoundError: Device not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json(
            "GET",
            f"/virtualconsole/{device_id}",
            params={"lastDate": last_date},
        )
        return [ConsoleLine.model_validate(item) for item in (data or [])]

    def send(self, device_id: str, command: str) -> None:
        """Write a command to the virtual console (operation ``addCommandToConsole``).

        The OpenAPI sends the command as a required query parameter, not a body.

        Args:
            device_id: Device UUID.
            command: Command string to execute on the device.

        Raises:
            NotFoundError: Device not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request(
            "PUT",
            f"/virtualconsole/{device_id}",
            params={"command": command},
        )
