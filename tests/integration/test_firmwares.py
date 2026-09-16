"""Live integration tests for OpenAPI tag Firmwares (TEST API only)."""

from __future__ import annotations

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_firmwares_list(api):
    """GET /firmwares — list firmware records.

    Args:
        api: Throttled live PosiverseClient fixture.
    """
    try:
        page = api.firmwares.list()
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"firmwares.list failed: {exc!r}"))
    assert page.items is not None
    assert len(page.items) >= 1


def test_firmwares_get(api, discovered_ids):
    """GET /firmwares/{firmwareId} — fetch one discovered firmware.

    Args:
        api: Throttled live PosiverseClient fixture.
        discovered_ids: Session-scoped discovered resource IDs.
    """
    firmware_id = discovered_ids.get("firmware_id")
    if not firmware_id:
        pytest.skip("no firmware id discovered from GET /firmwares")
    firmware = api.firmwares.get(firmware_id)
    assert firmware.id == firmware_id
