"""Live integration tests for OpenAPI tag Logs (TEST API only)."""

from __future__ import annotations

import time

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def _window_start_millis(days: int = 7) -> int:
    """Return a start timestamp in UTC millis for telemetry/user logs.

    Args:
        days: How far back from now to start the search window.

    Returns:
        Integer UTC millis since 1970-01-01.
    """
    return int(time.time() * 1000) - (days * 24 * 60 * 60 * 1000)


def test_logs_device(api, known_device_id, known_imei):
    """GET /devicelogs - search recent device logs for the known device.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
        known_imei: Known TEST device IMEI.
    """
    # Live TEST API expects millis for startMillis (OpenAPI text says seconds).
    start = _window_start_millis(14)
    try:
        page = api.call_with_retry(
            lambda: api.logs.list_device(
                start_millis=start,
                device_ids=known_device_id,
                limit=10,
            )
        )
    except Exception as exc:  # noqa: BLE001
        # Fall back to IMEI filter if deviceIds path is rejected.
        try:
            page = api.call_with_retry(
                lambda: api.logs.list_device(
                    start_millis=start,
                    imeis=known_imei,
                    limit=10,
                )
            )
        except Exception as exc2:  # noqa: BLE001
            pytest.fail(
                scrub_secrets(
                    f"logs.list_device failed for deviceIds and imeis: "
                    f"{exc!r} / {exc2!r}"
                )
            )
    assert page.items is not None


def test_logs_telemetry(api, known_imei):
    """GET /telemetrylogs - search recent telemetry for the known IMEI.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_imei: Known TEST device IMEI.
    """
    try:
        page = api.call_with_retry(
            lambda: api.logs.list_telemetry(
                start_millis=_window_start_millis(7),
                imeis=known_imei,
                limit=10,
            )
        )
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"logs.list_telemetry failed: {exc!r}"))
    assert page.items is not None


def test_logs_user(api, discovered_ids):
    """GET /userlogs - search recent user activity logs.

    Args:
        api: Throttled live PosiverseClient fixture.
        discovered_ids: Session-scoped discovered resource IDs.
    """
    user_id = discovered_ids.get("user_id")
    try:
        page = api.logs.list_user(
            start_millis=_window_start_millis(7),
            user_ids=user_id,
            limit=10,
        )
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"logs.list_user failed: {exc!r}"))
    assert page.items is not None
