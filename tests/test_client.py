"""Tests for the HTTP client helpers (JSON decode, dump_body)."""

from __future__ import annotations

import httpx
import pytest

from posiverse.client import HttpBody
from posiverse.models import DevicePut


def test_dump_body_excludes_none(client):
    """Pydantic PUT bodies omit unset/None fields."""
    payload = client.dump_body(DevicePut(name="A"))
    assert payload == {"name": "A"}


def test_empty_json_array_list(mock_api, client):
    """An empty JSON array is a valid paginated list."""
    mock_api.get("/products").mock(return_value=httpx.Response(200, json=[]))
    page = client.products.list()
    assert page.items == []


def test_non_array_list_raises(mock_api, client):
    """List endpoints that return a JSON object raise TypeError."""
    mock_api.get("/products").mock(return_value=httpx.Response(200, json={"id": "x"}))
    with pytest.raises(TypeError, match="JSON array"):
        client.products.list()


def test_decode_body_empty():
    """Empty responses decode to None."""
    response = httpx.Response(200, content=b"")
    assert HttpBody.decode(response) is None


def test_decode_body_text():
    """Non-JSON bodies are returned as text."""
    response = httpx.Response(200, text="ok", headers={"content-type": "text/plain"})
    assert HttpBody.decode(response) == "ok"
