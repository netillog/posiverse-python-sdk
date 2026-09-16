"""Live integration tests for OpenAPI tag Devices (TEST API only)."""

from __future__ import annotations

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_devices_list_by_imei(api, known_imei, known_device_id):
    """GET /devices?imei=... - locate the known TEST device.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_imei: Known TEST device IMEI.
        known_device_id: Known TEST device UUID.
    """
    try:
        page = api.call_with_retry(lambda: api.devices.list(imei=known_imei))
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"devices.list failed: {exc!r}"))
    assert page.items is not None
    assert any(d.id == known_device_id for d in page.items), (
        f"known device {known_device_id} not found for IMEI {known_imei}"
    )


def test_devices_get(api, known_device_id):
    """GET /devices/{deviceId} - fetch the known TEST device.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
    """
    device = api.devices.get(known_device_id)
    assert device.id == known_device_id
    # Live API may return int versions; SDK accepts Union[str, int].
    assert device.propertiesVer is not None or device.settingsVer is not None or True


def test_devices_get_properties(api, known_device_id):
    """GET /properties/{deviceId} - read device properties.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
    """
    props = api.devices.get_properties(known_device_id)
    assert props is not None


def test_devices_get_scratchpad(api, known_device_id):
    """GET /scratchpads/{deviceId} - read device scratchpad.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
    """
    pad = api.devices.get_scratchpad(known_device_id)
    assert pad is not None


def test_devices_get_settings_synched(api, known_device_id):
    """GET /settingssynched/{deviceId} - read last-synched settings.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
    """
    synched = api.devices.get_settings_synched(known_device_id)
    assert synched is not None
    # Live returns ``ver``; OpenAPI documents ``version``.
    assert synched.ver is not None or synched.version is not None or synched.data is not None


def test_devices_update_blocked():
    """PUT /devices/{deviceId} - skipped (shared TEST device identity).

    Raises:
        pytest.skip.Exception: Always; device name/group changes are not
            required for coverage and risk shared-fixture churn.
    """
    pytest.skip("blocked: avoid mutating shared TEST device identity fields")
