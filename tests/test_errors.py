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
from posiverse.errors import raise_for_status


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


def test_raise_for_status_ignores_2xx():
    """2xx statuses must not raise."""
    raise_for_status(200, {"ok": True})
    raise_for_status(204, None)


def test_error_message_from_plain_text():
    """String bodies are used as the exception message."""
    with pytest.raises(BadRequestError, match="nope") as info:
        raise_for_status(400, "nope")
    assert info.value.body == "nope"
