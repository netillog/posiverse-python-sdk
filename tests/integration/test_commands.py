"""Live integration tests for OpenAPI tag Commands (TEST API only).

Mutating command queue operations are exercised carefully: the only
documented example command is ``reset`` (device reboot), so add is
skipped. Delete of an empty/self-owned queue is allowed after list.
"""

from __future__ import annotations

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_commands_list(api, known_device_id):
    """GET /commands/{deviceId} — list pending commands for known device.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
    """
    try:
        commands = api.commands.list(known_device_id)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"commands.list failed: {exc!r}"))
    assert isinstance(commands, list)


def test_commands_add_blocked():
    """POST /commands/{deviceId} — skipped (documented example is reboot).

    Raises:
        pytest.skip.Exception: Always; OpenAPI example body is ``reset``,
            which reboots the device — not safe for automated live tests.
    """
    pytest.skip(
        "blocked: OpenAPI example command is 'reset' (device reboot); "
        "no documented non-destructive command for live add"
    )


def test_commands_delete_empty_queue(api, known_device_id, throttle):
    """DELETE /commands/{deviceId} — clear queue only when already empty.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
        throttle: Shared request throttle.
    """
    throttle.wait()
    pending = api.commands.list(known_device_id)
    if pending:
        pytest.skip(
            "blocked: pending commands exist on shared TEST device; "
            "refusing to delete unknown queue contents"
        )
    # Empty queue delete is a no-op / safe idempotent clear.
    api.commands.delete(known_device_id)
