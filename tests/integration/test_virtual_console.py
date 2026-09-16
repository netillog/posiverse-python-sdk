"""Live integration tests for OpenAPI tag VirtualConsole (TEST API only)."""

from __future__ import annotations

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_virtual_console_get_output(api, known_device_id):
    """GET /virtualconsole/{deviceId} — poll stored console lines.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
    """
    try:
        lines = api.virtual_console.get_output(known_device_id, last_date=0)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"virtual_console.get_output failed: {exc!r}"))
    assert isinstance(lines, list)


def test_virtual_console_send_blocked():
    """PUT /virtualconsole/{deviceId} — skipped (no safe documented command).

    Raises:
        pytest.skip.Exception: Always; console write executes on the device
            and no non-destructive command is documented for automation.
    """
    pytest.skip(
        "blocked: virtual console send executes on device; "
        "no documented non-destructive command for live send"
    )
