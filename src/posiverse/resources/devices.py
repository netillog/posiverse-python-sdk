"""Devices resource — OpenAPI tag Devices.

Paths:
    GET ``/devices``, GET/PUT ``/devices/{deviceId}``,
    GET ``/properties/{deviceId}``, GET ``/scratchpads/{deviceId}``,
    GET ``/settingssynched/{deviceId}``.
"""

from __future__ import annotations

from typing import Optional, Union

from posiverse.models import Device, DevicePut, Properties, Scratchpad, SettingsSynched
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource


class DevicesResource(BaseResource):
    """Read and update devices, plus properties, scratchpad, and synched settings."""

    def list(
        self,
        *,
        full: Optional[bool] = None,
        group_id: Optional[str] = None,
        imei: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> PaginatedResponse[Device]:
        """List devices (operation ``getDevices``).

        Args:
            full: When True, include nested settings, settingsSynched,
                properties, scratchpad, and full description (larger payload).
            group_id: Restrict results to devices in this group UUID.
            imei: Search for a device by IMEI.
            tenant_id: Alternate tenant UUID. Defaults to the account tenant.

        Returns:
            Paginated list of :class:`~posiverse.models.device.Device` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            "/devices",
            item_model=Device,
            params={
                "full": full,
                "groupId": group_id,
                "imei": imei,
                "tenantId": tenant_id,
            },
        )

    def get(self, device_id: str, *, full: Optional[bool] = None) -> Device:
        """Get a device by ID (operation ``getDevice``).

        Args:
            device_id: Device UUID.
            full: When True, include nested settings/properties/scratchpad.

        Returns:
            A :class:`~posiverse.models.device.Device` object.

        Raises:
            NotFoundError: Device not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json(
            "GET",
            f"/devices/{device_id}",
            params={"full": full},
        )
        return Device.model_validate(data)

    def update(self, device_id: str, body: Union[DevicePut, dict]) -> None:
        """Modify a device (operation ``modifyDevice``).

        Args:
            device_id: Device UUID.
            body: :class:`~posiverse.models.device.DevicePut` or dict of
                mutable fields (groupId, name, description, externalDeviceId).

        Raises:
            NotFoundError: Device not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request(
            "PUT",
            f"/devices/{device_id}",
            json=self._client.dump_body(body),
        )

    def get_properties(self, device_id: str) -> Properties:
        """Get device properties (operation ``getProperties``).

        Args:
            device_id: Device UUID.

        Returns:
            A :class:`~posiverse.models.properties.Properties` object.

        Raises:
            NotFoundError: Device not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/properties/{device_id}")
        return Properties.model_validate(data)

    def get_scratchpad(self, device_id: str) -> Scratchpad:
        """Get a device scratchpad (operation ``getScratchpad``).

        Args:
            device_id: Device UUID.

        Returns:
            A :class:`~posiverse.models.scratchpad.Scratchpad` object.

        Raises:
            NotFoundError: Device not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/scratchpads/{device_id}")
        return Scratchpad.model_validate(data)

    def get_settings_synched(self, device_id: str) -> SettingsSynched:
        """Get settings last synched from a device (operation ``getSettingsSynched``).

        Args:
            device_id: Device UUID.

        Returns:
            A :class:`~posiverse.models.settings.SettingsSynched` object.

        Raises:
            NotFoundError: Device not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/settingssynched/{device_id}")
        return SettingsSynched.model_validate(data)
