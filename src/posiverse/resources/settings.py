"""Settings resource — OpenAPI tag Settings.

Paths: GET/PUT /settings/{ownerId}
"""

from __future__ import annotations

from typing import Union

from posiverse.models import Settings, SettingsPut
from posiverse.resources._base import BaseResource


class SettingsResource(BaseResource):
    """Read and update expected settings for a device or group owner."""

    def get(self, owner_id: str) -> Settings:
        """Get settings for an owner (getSettings).

        Args:
            owner_id: Device or group UUID that owns the settings.

        Returns:
            Settings object.

        Raises:
            NotFoundError: Owner/settings not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/settings/{owner_id}")
        return Settings.model_validate(data)

    def update(self, owner_id: str, body: Union[SettingsPut, dict]) -> None:
        """Modify settings for an owner (modifySettings).

        Args:
            owner_id: Device or group UUID that owns the settings.
            body: SettingsPut model or dict of mutable settings sections.

        Raises:
            NotFoundError: Owner/settings not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        payload = (
            body.model_dump(exclude_none=True) if isinstance(body, SettingsPut) else body
        )
        self._client.request("PUT", f"/settings/{owner_id}", json=payload)
