"""Mocked tests for GET /devicelogs via list_device."""

from __future__ import annotations

import httpx

import posiverse
from posiverse.resources.logs import LogsResource


def test_list_device_validates_object_and_string_result(mock_api, client):
    """GET /devicelogs accepts object result payloads and string results."""
    mock_api.get("/devicelogs").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "deviceId": "d1",
                    "request": {"cmd": "ping"},
                    "result": {"status": "ok"},
                },
                {"deviceId": "d2", "request": "raw", "result": "ok"},
                {"deviceId": "d3", "request": None, "result": None},
            ],
        )
    )
    page = client.logs.list_device(start_millis=1, device_ids="d1")
    assert page.items[0].result == {"status": "ok"}
    assert page.items[0].request == {"cmd": "ping"}
    assert page.items[1].result == "ok"
    assert page.items[1].request == "raw"
    assert page.items[2].result is None
    assert page.items[2].request is None


def test_removed_log_helpers_are_not_public():
    """Convenience log helpers and their support types are not exported."""
    for name in ("get_logs", "get_reports", "get_device_data"):
        assert not hasattr(LogsResource, name)
    for name in ("DeviceLogQueries", "ReportIdentity"):
        assert name not in posiverse.__all__
        assert not hasattr(posiverse, name)


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
            json=[{"deviceId": "d1", "service": "config", "action": "logs", "request": "{}"}],
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
