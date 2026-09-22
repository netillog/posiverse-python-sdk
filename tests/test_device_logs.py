"""Mocked tests for device-log convenience filters and report dedupe."""

from __future__ import annotations

import json

import httpx
import pytest

from posiverse.device_logs import DeviceLogQueries, ReportIdentity
from posiverse.models import DeviceLog


def _report(ts, rpt, **fields) -> dict:
    """Build a device-log JSON row whose request carries ts and rpt."""
    body = {"ts": ts, "rpt": rpt}
    row = {"request": json.dumps(body)}
    row.update(fields)
    return row


def _params(request: httpx.Request) -> tuple[list[str], list[str]]:
    """Return (serviceIds, actions) from a mocked devicelogs request."""
    return (
        request.url.params.get_list("serviceIds"),
        request.url.params.get_list("actions"),
    )


def test_get_logs_filters_config_and_logs_action(mock_api, client):
    """get_logs sends serviceIds=config and actions=logs on GET /devicelogs."""
    captured = {}

    def respond(request: httpx.Request) -> httpx.Response:
        captured["services"], captured["actions"] = _params(request)
        assert request.url.params.get("imeis") == "123"
        assert request.url.params.get("startMillis") == "10"
        assert request.url.params.get("endMillis") == "20"
        assert request.url.params.get("limit") == "5"
        return httpx.Response(
            200,
            json=[{"deviceId": "d1", "service": "config", "action": "logs", "request": "{}"}],
        )

    mock_api.get("/devicelogs").mock(side_effect=respond)
    rows = client.logs.get_logs(start_millis=10, end_millis=20, imeis="123", limit=5)
    assert captured["services"] == [DeviceLogQueries.CONFIG_SERVICE]
    assert captured["actions"] == [DeviceLogQueries.LOGS_ACTION]
    assert rows[0].service == "config"
    assert rows[0].action == "logs"
    assert mock_api.calls.call_count == 1


def test_get_logs_follows_next_page(mock_api, client):
    """get_logs concatenates pages until x-next-page-url is absent."""

    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.params.get("cursor") == "2":
            return httpx.Response(200, json=[{"deviceId": "page-2", "action": "logs"}])
        return httpx.Response(
            200,
            json=[{"deviceId": "page-1", "action": "logs"}],
            headers={"x-next-page-url": "/devicelogs?cursor=2"},
        )

    mock_api.get("/devicelogs").mock(side_effect=respond)
    rows = client.logs.get_logs(start_millis=1, device_ids="dev-1")
    assert [row.deviceId for row in rows] == ["page-1", "page-2"]
    assert mock_api.calls.call_count == 2


def test_get_logs_stops_when_next_page_url_repeats(mock_api, client):
    """A repeated x-next-page-url does not walk forever."""

    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[{"deviceId": request.url.params.get("cursor") or "first"}],
            headers={"x-next-page-url": "/devicelogs?cursor=again"},
        )

    mock_api.get("/devicelogs").mock(side_effect=respond)
    rows = client.logs.get_logs(start_millis=1, imeis="123")
    assert [row.deviceId for row in rows] == ["first", "again"]
    assert mock_api.calls.call_count == 2


def test_get_logs_requires_exactly_one_device_selector(client):
    """get_logs uses the same imei XOR device id guard as list_device."""
    with pytest.raises(ValueError, match="exactly one"):
        client.logs.get_logs(start_millis=1)
    with pytest.raises(ValueError, match="exactly one"):
        client.logs.get_logs(start_millis=1, imeis="1", device_ids="d1")


def test_get_reports_uses_two_conjunctive_queries_and_dedupes(mock_api, client):
    """Reports are tel OR (conn AND new-sent/retry-sent), then deduped.

    The tel row is queried first, so it is kept when a conn row shares
    (ts, rpt) but differs in other fields. Key order in rpt does not matter.
    """
    seen: list[tuple[list[str], list[str]]] = []

    def respond(request: httpx.Request) -> httpx.Response:
        services, actions = _params(request)
        seen.append((services, actions))
        if services == ["tel"]:
            assert "actions" not in request.url.params
            return httpx.Response(
                200,
                json=[
                    _report(100, {"b": 2, "a": 1}, service="tel", result="from-tel"),
                    _report(200, "other", service="tel", result="unique-tel"),
                ],
            )
        if services == ["conn"]:
            assert actions == ["new-sent", "retry-sent"]
            return httpx.Response(
                200,
                json=[
                    _report(100, {"a": 1, "b": 2}, service="conn", action="new-sent", result="from-conn"),
                    _report(100, {"a": 1, "b": 2}, service="conn", action="retry-sent", result="retry"),
                    _report(300, "conn-only", service="conn", action="retry-sent", result="conn-only"),
                ],
            )
        raise AssertionError(f"unexpected filter {services} {actions}")

    mock_api.get("/devicelogs").mock(side_effect=respond)
    rows = client.logs.get_reports(start_millis=1, imeis=["123"])
    assert seen == [
        (["tel"], []),
        (["conn"], ["new-sent", "retry-sent"]),
    ]
    assert [(row.result, row.service) for row in rows] == [
        ("from-tel", "tel"),
        ("unique-tel", "tel"),
        ("conn-only", "conn"),
    ]


def test_get_device_data_unions_clauses_and_dedupes_report_subset(mock_api, client):
    """Device data is config/logs plus the report clauses, deduped once.

    A config log without ts/rpt is kept. A config log that does carry the
    pair wins over a later tel row with the same pair.
    """
    seen: list[tuple[list[str], list[str]]] = []

    def respond(request: httpx.Request) -> httpx.Response:
        services, actions = _params(request)
        seen.append((services, actions))
        if services == ["config"]:
            assert actions == ["logs"]
            return httpx.Response(
                200,
                json=[
                    {
                        "service": "config",
                        "action": "logs",
                        "request": "not-json",
                        "result": "diagnostic",
                    },
                    _report(7, "same", service="config", action="logs", result="config-report"),
                ],
            )
        if services == ["tel"]:
            return httpx.Response(
                200,
                json=[_report(7, "same", service="tel", result="tel-report")],
            )
        if services == ["conn"]:
            return httpx.Response(200, json=[])
        raise AssertionError(f"unexpected filter {services} {actions}")

    mock_api.get("/devicelogs").mock(side_effect=respond)
    rows = client.logs.get_device_data(start_millis=1, device_ids="dev-1")
    assert seen == [
        (["config"], ["logs"]),
        (["tel"], []),
        (["conn"], ["new-sent", "retry-sent"]),
    ]
    assert [row.result for row in rows] == ["diagnostic", "config-report"]


def test_report_identity_source_order_and_nulls():
    """request wins over result and extras; nulls and arrays are not keys."""
    request_wins = DeviceLog.model_validate(
        {
            "request": json.dumps({"ts": 2, "rpt": "from-request"}),
            "result": json.dumps({"ts": 9, "rpt": "from-result"}),
            "ts": 1,
            "rpt": "from-extra",
        }
    )
    assert ReportIdentity.extract(request_wins) == (2, "from-request")

    result_fallback = DeviceLog.model_validate(
        {"result": json.dumps({"ts": 9, "rpt": {"k": "v"}})}
    )
    assert ReportIdentity.extract(result_fallback) == (9, {"k": "v"})

    extra_only = DeviceLog.model_validate({"service": "tel", "ts": 4, "rpt": "top"})
    assert ReportIdentity.extract(extra_only) == (4, "top")

    nulls = DeviceLog.model_validate({"request": json.dumps({"ts": None, "rpt": "x"})})
    array = DeviceLog.model_validate(
        {"request": json.dumps([{"ts": 1, "rpt": "a"}, {"ts": 2, "rpt": "b"}])}
    )
    missing = DeviceLog.model_validate({"request": json.dumps({"ts": 1})})
    assert ReportIdentity.extract(nulls) is None
    assert ReportIdentity.extract(array) is None
    assert ReportIdentity.extract(missing) is None

    deduped = ReportIdentity.dedupe([nulls, nulls, missing])
    assert len(deduped) == 3


def test_report_identity_keeps_first_when_duplicates_differ():
    """Same (ts, rpt) with different sibling fields keeps the earlier row.

    Object key order is not a distinct identity. Integer ``1`` and string
    ``"1"`` are distinct.
    """
    first = DeviceLog.model_validate(_report(1, {"z": 1, "a": 2}, result="keep"))
    second = DeviceLog.model_validate(_report(1, {"a": 2, "z": 1}, result="drop"))
    other = DeviceLog.model_validate(_report(1, {"a": 3}, result="other"))
    string_ts = DeviceLog.model_validate(_report("1", {"z": 1, "a": 2}, result="string-ts"))
    plain = DeviceLog.model_validate({"service": "config", "action": "logs", "request": "line"})
    kept = ReportIdentity.dedupe([plain, first, second, other, string_ts, plain])
    assert [row.result for row in kept] == [None, "keep", "other", "string-ts", None]
    assert kept[0].request == "line"
    assert kept[-1].request == "line"
