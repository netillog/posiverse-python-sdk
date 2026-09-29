"""Mocked tests for GET /devicelogs via list_device."""

from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError


def test_list_device_validates_object_result(mock_api, client):
    """GET /devicelogs accepts object request/result payloads and null."""
    mock_api.get("/devicelogs").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "deviceId": "d1",
                    "database": "db-1",
                    "request": {"cmd": "ping"},
                    "result": {"status": "ok"},
                },
                {"deviceId": "d3", "request": None, "result": None},
            ],
        )
    )
    page = client.logs.list_device(start_millis=1, device_ids="d1")
    assert page.items[0].result == {"status": "ok"}
    assert page.items[0].request == {"cmd": "ping"}
    assert page.items[0].database == "db-1"
    assert page.items[1].result is None
    assert page.items[1].request is None


def test_list_device_rejects_string_result(mock_api, client):
    """OpenAPI types request and result as objects, so a string fails validation."""
    mock_api.get("/devicelogs").mock(
        return_value=httpx.Response(
            200,
            json=[{"deviceId": "d2", "request": "raw", "result": "ok"}],
        )
    )
    with pytest.raises(ValidationError):
        client.logs.list_device(device_ids="d2")


def test_list_device_sends_service_ids_and_actions(mock_api, client):
    """list_device forwards serviceIds and actions on GET /devicelogs."""
    captured = {}

    def respond(request: httpx.Request) -> httpx.Response:
        captured["services"] = request.url.params.get_list("serviceIds")
        captured["actions"] = request.url.params.get_list("actions")
        assert request.url.params.get("imeis") == "123"
        assert request.url.params.get("startMillis") == "10"
        assert request.url.params.get("endMillis") == "20"
        assert request.url.params.get("limit") == "5"
        return httpx.Response(
            200,
            json=[{"deviceId": "d1", "service": "config", "action": "logs", "request": {}}],
        )

    mock_api.get("/devicelogs").mock(side_effect=respond)
    page = client.logs.list_device(
        start_millis=10,
        end_millis=20,
        imeis="123",
        service_ids=["config"],
        actions=["logs"],
        limit=5,
    )
    assert captured["services"] == ["config"]
    assert captured["actions"] == ["logs"]
    assert page.items[0].service == "config"
    assert page.items[0].action == "logs"
    assert mock_api.calls.call_count == 1
