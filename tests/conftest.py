"""Shared pytest fixtures for Posiverse SDK unit tests.

All HTTP traffic is mocked with respx. An autouse fixture refuses any
request whose host is the production Posiverse OpenAPI. No secrets are
used; the fake API key is not a credential.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from posiverse import PROD_BASE_URL, PosiverseClient
from posiverse._env import load_dotenv
from posiverse.config import PosiverseConfig

# Before live gates / API key checks (including import-time skipif).
# Shell and CI values already in the environment are left unchanged.
load_dotenv()

FAKE_API_KEY = "test-api-key-not-a-secret"
PROD_HOST = "openapi-prod.posiverse.com"
# Reserved invalid TLD so mocked unit tests never contact a real host.
MOCK_BASE_URL = "https://openapi.mock.invalid"


@pytest.fixture(autouse=True)
def _isolate_override_env(request, monkeypatch):
    """Keep unit tests from inheriting a developer POSIVERSE_BASE_URL.

    Live tests must see the real environment so they can require the override.

    Args:
        request: Current pytest item.
        monkeypatch: Pytest monkeypatch fixture.
    """
    if request.node.get_closest_marker("live"):
        return
    monkeypatch.delenv(PosiverseConfig.BASE_URL_ENV, raising=False)


@pytest.fixture(autouse=True)
def _refuse_production_host(monkeypatch):
    """Fail the test run if any request targets the production OpenAPI host.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    original = httpx.Client.send

    def guarded(self, request, *args, **kwargs):  # noqa: ANN001
        if request.url.host == PROD_HOST:
            raise RuntimeError(
                "Refusing to call production Posiverse API from tests: "
                f"{request.url} (PROD_BASE_URL={PROD_BASE_URL})"
            )
        return original(self, request, *args, **kwargs)

    monkeypatch.setattr(httpx.Client, "send", guarded)


@pytest.fixture
def api_key() -> str:
    """Return a fake API key for unit tests."""
    return FAKE_API_KEY


@pytest.fixture
def base_url() -> str:
    """Return a mock https base URL (never production, never a live host)."""
    return MOCK_BASE_URL


@pytest.fixture
def client(api_key: str, base_url: str):
    """Yield a PosiverseClient bound to the mocked server.

    Args:
        api_key: Fake API key fixture.
        base_url: Mock server URL fixture.
    """
    with PosiverseClient(api_key=api_key, base_url=base_url) as c:
        yield c


@pytest.fixture
def mock_api(base_url: str):
    """Activate a respx mock router scoped to the mock base URL.

    Args:
        base_url: Mock server URL fixture.
    """
    with respx.mock(
        base_url=base_url,
        assert_all_called=False,
        assert_all_mocked=True,
    ) as router:
        yield router
