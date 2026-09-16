"""Optional live smoke test against an internal Posiverse OpenAPI.

This module is skipped unless ``POSIVERSE_API_KEY`` is set and either
``POSIVERSE_LIVE_SMOKE=1`` or ``POSIVERSE_LIVE_INTEGRATION=1`` is set.
``POSIVERSE_BASE_URL`` is required and must not be the production host.
CI does not enable this marker.
"""

from __future__ import annotations

import os

import pytest

from posiverse import PosiverseClient
from tests.live_guard import LiveTestGuard


def _live_gate_enabled() -> bool:
    """Return True when either live smoke or live integration is enabled."""
    return LiveTestGuard.smoke_or_integration_enabled()


pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not _live_gate_enabled(),
        reason=(
            "live smoke disabled (set POSIVERSE_LIVE_SMOKE=1 or "
            "POSIVERSE_LIVE_INTEGRATION=1 to enable)"
        ),
    ),
]


def test_live_list_tenants_on_override_server_only():
    """Call GET /tenants on the POSIVERSE_BASE_URL host when enabled.

    Raises:
        pytest.skip: If POSIVERSE_API_KEY or POSIVERSE_BASE_URL is not set.
        RuntimeError: If the override URL is the production host.
    """
    if not os.environ.get("POSIVERSE_API_KEY"):
        pytest.skip("POSIVERSE_API_KEY is required for live smoke")

    base_url = LiveTestGuard.require_base_url()
    with PosiverseClient(base_url=base_url) as client:
        assert client.base_url == base_url
        LiveTestGuard.assert_not_production(client.base_url)
        page = client.tenants.list()
        assert page.items is not None
