"""Optional live smoke test against the Posiverse TEST OpenAPI only.

This module is skipped unless ``POSIVERSE_API_KEY`` is set and either
``POSIVERSE_LIVE_SMOKE=1`` or ``POSIVERSE_LIVE_INTEGRATION=1`` is set.
It always uses ``https://openapi-test.posiverse.com`` and never the
production host. CI does not enable this marker.
"""

from __future__ import annotations

import os

import pytest

from posiverse import TEST_BASE_URL, PosiverseClient

def _live_gate_enabled() -> bool:
    """Return True when either live smoke or live integration is enabled.

    Returns:
        True if ``POSIVERSE_LIVE_SMOKE=1`` or ``POSIVERSE_LIVE_INTEGRATION=1``.
    """
    return (
        os.environ.get("POSIVERSE_LIVE_SMOKE") == "1"
        or os.environ.get("POSIVERSE_LIVE_INTEGRATION") == "1"
    )


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


def test_live_list_tenants_on_test_server_only():
    """Call GET /tenants on the test server when explicitly enabled.

    Raises:
        pytest.skip: If POSIVERSE_API_KEY is not set.
        AssertionError: If the client base URL is not the test server.
    """
    if not os.environ.get("POSIVERSE_API_KEY"):
        pytest.skip("POSIVERSE_API_KEY is required for live smoke")

    # HARD CONSTRAINT: never point live tests at production.
    assert TEST_BASE_URL == "https://openapi-test.posiverse.com"
    with PosiverseClient(base_url=TEST_BASE_URL) as client:
        assert client.base_url == TEST_BASE_URL
        assert "openapi-prod" not in client.base_url
        page = client.tenants.list()
        assert page.items is not None
