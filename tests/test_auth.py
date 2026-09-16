"""Tests for API key authentication header behavior."""

from __future__ import annotations

import httpx
import pytest

from posiverse import AUTH_HEADER, TEST_BASE_URL, PosiverseClient
from posiverse.client import API_KEY_ENV


def test_auth_header_sent_on_requests(mock_api, client, api_key):
    """Every request must include the posiverse-auth-key header (not Bearer)."""
    route = mock_api.get("/devices").mock(
        return_value=httpx.Response(200, json=[], headers={"x-total-count": "0"})
    )
    client.devices.list()
    assert route.called
    request = route.calls.last.request
    assert request.headers.get(AUTH_HEADER) == api_key
    assert "Authorization" not in request.headers or not request.headers.get(
        "Authorization", ""
    ).lower().startswith("bearer")


def test_api_key_from_env(monkeypatch, mock_api):
    """Client reads POSIVERSE_API_KEY when api_key argument is omitted."""
    monkeypatch.setenv(API_KEY_ENV, "env-key-value")
    route = mock_api.get("/tenants").mock(
        return_value=httpx.Response(200, json=[], headers={"x-total-count": "0"})
    )
    with PosiverseClient(base_url=TEST_BASE_URL) as client:
        client.tenants.list()
    assert route.calls.last.request.headers.get(AUTH_HEADER) == "env-key-value"


def test_missing_api_key_raises(monkeypatch):
    """Client raises ValueError when no key is provided or in the environment."""
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    with pytest.raises(ValueError, match="API key required"):
        PosiverseClient(base_url=TEST_BASE_URL)


def test_default_base_url_is_test():
    """Default client base URL must be the test server, not production."""
    with PosiverseClient(api_key="k") as client:
        assert client.base_url == TEST_BASE_URL
        assert "openapi-prod" not in client.base_url
