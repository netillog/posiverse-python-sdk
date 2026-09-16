"""Tests for pagination header parsing on list responses."""

from __future__ import annotations

import httpx


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
