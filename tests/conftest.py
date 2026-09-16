"""Shared pytest fixtures for Posiverse SDK unit tests.

All HTTP traffic is mocked with respx against the test base URL only.
No secrets and no production endpoints are used.
"""

from __future__ import annotations

import pytest
import respx

from posiverse import TEST_BASE_URL, PosiverseClient

FAKE_API_KEY = "test-api-key-not-a-secret"


@pytest.fixture
def api_key() -> str:
    """Return a fake API key for unit tests."""
    return FAKE_API_KEY


@pytest.fixture
def base_url() -> str:
    """Return the test server base URL (never production)."""
    return TEST_BASE_URL


@pytest.fixture
def client(api_key: str, base_url: str):
    """Yield a PosiverseClient bound to the mocked test server."""
    with PosiverseClient(api_key=api_key, base_url=base_url) as c:
        yield c


@pytest.fixture
def mock_api(base_url: str):
    """Activate a respx mock router scoped to the test base URL."""
    with respx.mock(base_url=base_url, assert_all_called=False) as router:
        yield router
