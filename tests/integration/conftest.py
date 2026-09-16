"""Pytest fixtures for live Posiverse integration tests.

The live client is constructed only when the env gate is set. It requires
``POSIVERSE_BASE_URL`` and refuses the production OpenAPI host. A shared
throttle keeps calls under the observed rate limit (2 requests/second/tenant).
"""

from __future__ import annotations

import os

import pytest

from posiverse import PosiverseClient
from posiverse.config import PosiverseConfig
from tests.integration.helpers import (
    KNOWN_TEST_DEVICE_ID,
    KNOWN_TEST_IMEI,
    RequestThrottle,
    assert_not_production_base_url,
    call_with_retry,
    live_integration_enabled,
    load_release_mask,
)
from tests.live_guard import LiveTestGuard

# Apply the live marker to every test under tests/integration/.
pytestmark = pytest.mark.live


def pytest_collection_modifyitems(config, items):  # noqa: ANN001
    """Skip integration module tests unless the live env gate is set.

    Args:
        config: Pytest config object.
        items: Collected test items (mutated in place).
    """
    if live_integration_enabled():
        return
    skip = pytest.mark.skip(
        reason=(
            "live integration disabled "
            "(set POSIVERSE_LIVE_INTEGRATION=1 to enable; "
            "POSIVERSE_LIVE_SMOKE=1 also accepted)"
        )
    )
    for item in items:
        if "/integration/" in str(item.fspath).replace("\\", "/"):
            item.add_marker(skip)


@pytest.fixture(scope="session")
def release_mask():
    """Load Release.json mask constraints for settings write tests.

    Returns:
        The ``mask`` mapping from the checked-in Release.json fixture.
    """
    return load_release_mask()


@pytest.fixture(scope="session")
def throttle() -> RequestThrottle:
    """Session-scoped request throttle for the live API rate limit.

    Returns:
        A :class:`RequestThrottle` shared by all live tests in the session.
    """
    return RequestThrottle()


@pytest.fixture(scope="session")
def live_client(throttle: RequestThrottle):
    """Yield a PosiverseClient bound to ``POSIVERSE_BASE_URL``.

    Args:
        throttle: Shared request throttle fixture.

    Yields:
        A :class:`PosiverseClient` using the required override URL.

    Raises:
        pytest.skip.Exception: If the live gate, API key, or base URL is unset.
        RuntimeError: If the override URL is the production host.
    """
    if not live_integration_enabled():
        pytest.skip("live integration gate not set")
    if not os.environ.get(PosiverseConfig.API_KEY_ENV):
        pytest.skip("POSIVERSE_API_KEY is required for live integration")

    base_url = LiveTestGuard.require_base_url()
    with PosiverseClient(base_url=base_url) as client:
        assert_not_production_base_url(client.base_url)
        assert client.base_url == base_url
        # Bind throttle helper onto the client for test convenience.
        client._live_throttle = throttle  # type: ignore[attr-defined]
        yield client


@pytest.fixture
def api(live_client: PosiverseClient, throttle: RequestThrottle):
    """Return the live client after waiting for the rate-limit throttle.

    Args:
        live_client: Session-scoped live client.
        throttle: Shared request throttle.

    Returns:
        The live :class:`PosiverseClient`.
    """
    throttle.wait()
    # Expose retry helper for tests that need multi-call resilience.
    live_client.call_with_retry = lambda fn, retries=5: call_with_retry(  # type: ignore[attr-defined]
        throttle, fn, retries=retries
    )
    return live_client


@pytest.fixture(scope="session")
def known_device_id() -> str:
    """Return the known TEST device UUID.

    Returns:
        Device UUID string.
    """
    return KNOWN_TEST_DEVICE_ID


@pytest.fixture(scope="session")
def known_imei() -> str:
    """Return the known TEST device IMEI.

    Returns:
        IMEI string.
    """
    return KNOWN_TEST_IMEI


@pytest.fixture(scope="session")
def discovered_ids(live_client: PosiverseClient, throttle: RequestThrottle):
    """Discover Group/Tenant/User/Product/Firmware IDs from the live API.

    Args:
        live_client: Session-scoped live client.
        throttle: Shared request throttle.

    Returns:
        Dict with optional keys ``tenant_id``, ``group_id``, ``user_id``,
        ``product_id``, ``firmware_id``, ``tag_id``.
    """
    ids: dict = {}

    def _first_id(page):  # noqa: ANN001
        if page.items:
            return getattr(page.items[0], "id", None)
        return None

    tenants = call_with_retry(throttle, live_client.tenants.list)
    ids["tenant_id"] = _first_id(tenants)

    groups = call_with_retry(throttle, live_client.groups.list)
    ids["group_id"] = _first_id(groups)

    users = call_with_retry(throttle, live_client.users.list)
    ids["user_id"] = _first_id(users)

    products = call_with_retry(throttle, live_client.products.list)
    ids["product_id"] = _first_id(products)

    firmwares = call_with_retry(throttle, live_client.firmwares.list)
    ids["firmware_id"] = _first_id(firmwares)

    tags = call_with_retry(throttle, live_client.tags.list)
    ids["tag_id"] = _first_id(tags)

    return ids
