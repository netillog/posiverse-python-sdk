"""Live integration tests for OpenAPI tag Settings (TEST API only).

Mutating writes are limited to the known TEST device, constrained by
Release.json mask metadata, and restored afterward.
"""

from __future__ import annotations

import pytest

from tests.integration.helpers import (
    ALLOWED_SETTINGS_MASK_KEYS,
    field_constraints,
    pick_alternate_int,
    scrub_secrets,
    settings_section_dict,
)

pytestmark = pytest.mark.live


def test_settings_get(api, known_device_id):
    """GET /settings/{ownerId} - read expected settings for known device.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID (ownerId).
    """
    try:
        settings = api.settings.get(known_device_id)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"settings.get failed: {exc!r}"))
    assert settings is not None


def test_settings_update_bluetooth_scan_restore(api, known_device_id, release_mask, throttle):
    """PUT /settings/{ownerId} - reversible bluetooth.scan change + restore.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
        release_mask: Release.json mask fixture.
        throttle: Shared request throttle (extra waits around restore).
    """
    assert "bluetooth" in ALLOWED_SETTINGS_MASK_KEYS
    constraints = field_constraints(release_mask, "bluetooth", "scan")
    assert constraints.get("type") == "int"
    assert constraints.get("min") == 0
    assert constraints.get("max") == 30

    original = api.settings.get(known_device_id)
    bluetooth = settings_section_dict(original, "bluetooth")
    current_scan = bluetooth.get("scan")
    if current_scan is not None:
        current_scan = int(current_scan)
    new_scan = pick_alternate_int(current_scan, constraints)
    if current_scan is not None and new_scan == current_scan:
        pytest.skip("bluetooth.scan has no alternate in-range value")

    try:
        throttle.wait()
        api.settings.update(known_device_id, {"bluetooth": {"scan": new_scan}})
        throttle.wait()
        after = api.settings.get(known_device_id)
        after_scan = settings_section_dict(after, "bluetooth").get("scan")
        assert after_scan is not None
        assert int(after_scan) == new_scan
    finally:
        # Restore prior value when we had one; otherwise restore default.
        restore_value = (
            int(current_scan)
            if current_scan is not None
            else int(constraints.get("default", 0))
        )
        throttle.wait()
        try:
            api.settings.update(known_device_id, {"bluetooth": {"scan": restore_value}})
        except Exception as exc:  # noqa: BLE001
            pytest.fail(scrub_secrets(f"settings restore failed: {exc!r}"))
