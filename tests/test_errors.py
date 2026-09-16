"""Tests for HTTP status → typed exception mapping."""

from __future__ import annotations

import httpx
import pytest

from posiverse import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
)


@pytest.mark.parametrize(
    ("status", "exc_cls"),
    [
        (400, BadRequestError),
        (401, AuthenticationError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, APIError),
    ],
)
def test_error_mapping(mock_api, client, status, exc_cls):
    """Non-2xx responses raise the matching typed APIError subclass."""
    mock_api.get("/devices/missing").mock(
        return_value=httpx.Response(
            status,
            json={"code": status, "message": f"error-{status}"},
        )
    )
    with pytest.raises(exc_cls) as info:
        client.devices.get("missing")
    assert info.value.status_code == status
    assert "error-" in str(info.value)
