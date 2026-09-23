"""Convenience filters and report dedupe for ``GET /devicelogs``.

The OpenAPI operation ``getDeviceLogs`` has no boolean filter language.
``serviceIds`` and ``actions`` are independent query parameters. This
module names the conjunctive clauses the convenience methods send and
deduplicates report-shaped rows after those calls are merged.

Hypothesis — filter semantics
    ``serviceIds`` means "services to include" (OR within the array) and
    ``actions`` means "actions to include" (OR within the array). When
    both are present they are ANDed: a row must match one listed service
    and one listed action. Nothing in the spec expresses
    ``(service=tel) OR (service=conn AND action in [new-sent, retry-sent])``
    as a single request. ``andTerms`` / ``orTerms`` are substring searches
    of the log text, not field predicates, so they are not used here.

Hypothesis — payload shape
    ``DeviceLog`` has no ``ts`` or ``rpt`` properties. OpenAPI types
    ``request`` and ``result`` as JSON strings; live responses may send
    either as a JSON object or null. Report identity is taken from the
    first JSON *object* that contains both keys, non-null:

    1. ``request`` (the device payload)
    2. ``result``
    3. extra top-level fields kept by the model

    A JSON array is not treated as one report and is not exploded.
    Nested objects are not searched. ``logs[].msg`` is not searched.
    Config rows (``service=config``, ``action=logs``) usually lack the
    pair and are kept as-is.
"""

from __future__ import annotations

import json
from typing import Any, Optional, Sequence

from posiverse.models.logs import DeviceLog


class DeviceLogQueries:
    """``serviceIds`` / ``actions`` values for the convenience searches.

    Each pair is one ``GET /devicelogs`` request. See the module docstring
    for why reports and device data are more than one request.
    """

    CONFIG_SERVICE = "config"
    LOGS_ACTION = "logs"
    TEL_SERVICE = "tel"
    CONN_SERVICE = "conn"
    CONN_REPORT_ACTIONS = ("new-sent", "retry-sent")


class ReportIdentity:
    """Find ``(ts, rpt)`` on a device log and collapse duplicate reports.

    Duplicate policy: the earlier row in the input sequence is kept.
    A later row with the same canonical pair is dropped even when other
    fields differ. Rows that are not report-shaped are always kept, in
    order, and are not compared to each other.

    Callers choose the sequence order. :meth:`posiverse.resources.logs.LogsResource.get_reports`
    places every ``service=tel`` row before ``service=conn`` rows, so a
    telemetry row wins over a connection send/retry of the same report.
    :meth:`~posiverse.resources.logs.LogsResource.get_device_data` places
    config logs before that report sequence, so a config row that itself
    carries ``ts`` and ``rpt`` wins over a later report with the same pair.

    Canonical form is JSON with object keys sorted. ``{"a": 1, "b": 2}``
    matches ``{"b": 2, "a": 1}``. Integer ``1`` does not match float
    ``1.0`` or string ``"1"``. List order is significant.
    """

    @staticmethod
    def extract(log: DeviceLog) -> Optional[tuple[Any, Any]]:
        """Return ``(ts, rpt)`` when ``log`` is report-shaped.

        Args:
            log: A device log row from ``GET /devicelogs``.

        Returns:
            The first non-null ``(ts, rpt)`` pair from ``request``, then
            ``result``, then extra top-level fields. ``None`` when no
            such pair exists.
        """
        for candidate in (log.request, log.result):
            pair = ReportIdentity._pair_from_payload(candidate)
            if pair is not None:
                return pair
        return ReportIdentity._pair_from_payload(log.model_extra)

    @staticmethod
    def canonical(ts: Any, rpt: Any) -> tuple[str, str]:
        """Return a hashable identity for one ``(ts, rpt)`` pair.

        Args:
            ts: Report timestamp value (any JSON-like object).
            rpt: Report body or type (any JSON-like object).

        Returns:
            Two JSON strings. Object keys are sorted so key order does
            not create a distinct identity.
        """
        return (ReportIdentity._freeze(ts), ReportIdentity._freeze(rpt))

    @staticmethod
    def dedupe(logs: Sequence[DeviceLog]) -> list[DeviceLog]:
        """Keep one row per unique ``(ts, rpt)`` pair.

        Args:
            logs: Device log rows in the order they should be preferred.
                The first row for a given pair is the one that is kept.

        Returns:
            A new list. Non-report rows stay in place. The first report
            row for each canonical pair stays; later matches are omitted
            even if their other fields differ.
        """
        kept: list[DeviceLog] = []
        seen: set[tuple[str, str]] = set()
        for log in logs:
            pair = ReportIdentity.extract(log)
            if pair is None:
                kept.append(log)
                continue
            key = ReportIdentity.canonical(pair[0], pair[1])
            if key in seen:
                continue
            seen.add(key)
            kept.append(log)
        return kept

    @staticmethod
    def _freeze(value: Any) -> str:
        """Serialize ``value`` to a stable JSON string.

        Args:
            value: JSON-like value used as part of a report identity.

        Returns:
            Compact JSON with sorted object keys. Non-JSON values fall
            back to ``str`` so a single odd payload cannot abort dedupe.
        """
        return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

    @staticmethod
    def _pair_from_payload(payload: Any) -> Optional[tuple[Any, Any]]:
        """Read ``ts`` and ``rpt`` from a JSON object or JSON string.

        Args:
            payload: A string, mapping, or other value stored on a log.

        Returns:
            ``(ts, rpt)`` when both keys exist and neither value is
            ``None``. ``None`` for blank strings, invalid JSON, arrays,
            and objects that lack either key.
        """
        if isinstance(payload, str):
            text = payload.strip()
            if not text:
                return None
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                return None
        if not isinstance(payload, dict):
            return None
        if "ts" not in payload or "rpt" not in payload:
            return None
        ts = payload["ts"]
        rpt = payload["rpt"]
        if ts is None or rpt is None:
            return None
        return ts, rpt
