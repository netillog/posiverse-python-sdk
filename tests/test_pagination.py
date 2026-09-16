"""Tests for pagination header parsing on list responses."""

from __future__ import annotations

import httpx

from posiverse.models import Device
from posiverse.pagination import PaginatedResponse, pagination_from_headers


def test_pagination_headers(mock_api, client):
    """List responses expose x-total-count / page-count / page-start / next-page-url."""
    mock_api.get("/devices").mock(
        return_value=httpx.Response(
            200,
            json=[{"id": "d1", "name": "One"}],
            headers={
                "x-total-count": "42",
                "x-page-count": "1",
                "x-page-start": "0",
                "x-next-page-url": "/devices?page=2",
            },
        )
    )
    page = client.devices.list()
    assert page.total_count == 42
    assert page.page_count == 1
    assert page.page_start == 0
    assert page.next_page_url == "/devices?page=2"
    assert page.has_next_page is True
    assert len(page.items) == 1
    assert page.items[0].id == "d1"
    assert page.absolute_next_page_url(client.base_url) == (f"{client.base_url}/devices?page=2")


def test_pagination_without_next(mock_api, client):
    """Missing x-next-page-url means no further pages."""
    mock_api.get("/groups").mock(
        return_value=httpx.Response(
            200,
            json=[],
            headers={
                "x-total-count": "0",
                "x-page-count": "0",
                "x-page-start": "0",
            },
        )
    )
    page = client.groups.list()
    assert page.next_page_url is None
    assert page.has_next_page is False
    assert client.follow_next_page(page, Device) is None


def _devices_pages(request: httpx.Request) -> httpx.Response:
    """Return page 1 or 2 based on the ``page`` query argument."""
    if request.url.params.get("page") == "2":
        return httpx.Response(200, json=[{"id": "d2"}], headers={"x-total-count": "2"})
    return httpx.Response(
        200,
        json=[{"id": "d1"}],
        headers={"x-next-page-url": "/devices?page=2", "x-total-count": "2"},
    )


def test_follow_next_page(mock_api, client):
    """follow_next_page requests the partial x-next-page-url on the test host."""
    mock_api.get("/devices").mock(side_effect=_devices_pages)
    first = client.devices.list()
    assert first.items[0].id == "d1"
    second = client.follow_next_page(first, Device)
    assert second is not None
    assert second.items[0].id == "d2"


def test_iter_pages(mock_api, client):
    """iter_pages walks x-next-page-url until it is absent."""
    mock_api.get("/devices").mock(side_effect=_devices_pages)
    pages = list(client.iter_pages("GET", "/devices", item_model=Device))
    assert [p.items[0].id for p in pages] == ["d1", "d2"]


def test_pagination_from_headers_invalid_int():
    """Non-integer pagination headers become None rather than raising."""
    meta = pagination_from_headers(
        {"x-total-count": "nope", "x-page-count": "", "x-next-page-url": ""}
    )
    assert meta["total_count"] is None
    assert meta["page_count"] is None
    assert meta["next_page_url"] is None


def test_paginated_response_defaults():
    """PaginatedResponse can be constructed with only items."""
    page = PaginatedResponse[Device](items=[])
    assert page.has_next_page is False
