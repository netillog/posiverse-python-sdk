"""Firmwares resource — OpenAPI tag Firmwares.

Paths: GET ``/firmwares``, GET ``/firmwares/{firmwareId}``.
"""

from __future__ import annotations

from typing import Optional

from posiverse.models import Firmware
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource


class FirmwaresResource(BaseResource):
    """List and fetch firmware records."""

    def list(self, *, tenant_id: Optional[str] = None) -> PaginatedResponse[Firmware]:
        """List firmwares (operation ``getFirmwares``).

        Args:
            tenant_id: Alternate tenant UUID.

        Returns:
            Paginated list of :class:`~posiverse.models.firmware.Firmware` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            "/firmwares",
            item_model=Firmware,
            params={"tenantId": tenant_id},
        )

    def get(self, firmware_id: str) -> Firmware:
        """Get a firmware by ID (operation ``getFirmware``).

        Args:
            firmware_id: Firmware UUID.

        Returns:
            A :class:`~posiverse.models.firmware.Firmware` object.

        Raises:
            NotFoundError: Firmware not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/firmwares/{firmware_id}")
        return Firmware.model_validate(data)
