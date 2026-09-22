"""Logs resource — OpenAPI tag Logs.

Paths: GET ``/devicelogs``, GET ``/telemetrylogs``, GET ``/userlogs``.

``get_logs``, ``get_reports``, and ``get_device_data`` call ``getDeviceLogs``
only. They do not add endpoints. Reports and device data issue more than
one request because the spec cannot express their OR filters in one query.
See :mod:`posiverse.device_logs`.
"""

from __future__ import annotations

from typing import Optional, Sequence, Union

from posiverse._utils import as_list
from posiverse.device_logs import DeviceLogQueries, ReportIdentity
from posiverse.models import DeviceLog, TelemetryLog, UserLog
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource

StrList = Union[str, Sequence[str]]


class LogsResource(BaseResource):
    """Query device, telemetry, and user activity logs."""

    def list_device(
        self,
        *,
        start_millis: int,
        imeis: Optional[StrList] = None,
        device_ids: Optional[StrList] = None,
        service_ids: Optional[StrList] = None,
        actions: Optional[StrList] = None,
        end_millis: Optional[int] = None,
        and_terms: Optional[StrList] = None,
        or_terms: Optional[StrList] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[DeviceLog]:
        """Search device logs (operation ``getDeviceLogs``).

        The OpenAPI marks both ``imeis`` and ``deviceIds`` as required, but
        the descriptions state that exactly one of the two may be provided.
        This method enforces that XOR in Python before calling the API.

        Args:
            start_millis: Start of the search window. The OpenAPI describes
                this as UTC seconds since 1970-01-01, limited to the past
                40 days (parameter name remains ``startMillis``).
            imeis: One IMEI (or a sequence). Mutually exclusive with
                ``device_ids``.
            device_ids: One device UUID (or a sequence). Mutually exclusive
                with ``imeis``.
            service_ids: Services to include (``config``, ``tel``,
                ``firmware``, ``ephemeris``, ``certs``, ``open_api``,
                ``api``, ``conn``).
            actions: Action name filters.
            end_millis: End of the search window; defaults to now on the server.
            and_terms: Strings that must all appear in a log.
            or_terms: Strings of which at least one must appear in a log.
            limit: Maximum logs to return (server default 1000, max 100000).

        Returns:
            Paginated list of :class:`~posiverse.models.logs.DeviceLog` objects.

        Raises:
            ValueError: If neither or both of ``imeis`` and ``device_ids``
                are provided.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        imei_list = as_list(imeis)
        device_id_list = as_list(device_ids)
        if bool(imei_list) == bool(device_id_list):
            raise ValueError("Provide exactly one of imeis or device_ids")
        return self._client.request_paginated(
            "GET",
            "/devicelogs",
            item_model=DeviceLog,
            params={
                "imeis": imei_list,
                "deviceIds": device_id_list,
                "serviceIds": as_list(service_ids),
                "actions": as_list(actions),
                "startMillis": start_millis,
                "endMillis": end_millis,
                "andTerms": as_list(and_terms),
                "orTerms": as_list(or_terms),
                "limit": limit,
            },
        )

    def get_logs(
        self,
        *,
        start_millis: int,
        imeis: Optional[StrList] = None,
        device_ids: Optional[StrList] = None,
        end_millis: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[DeviceLog]:
        """Return device logs for ``service=config`` and ``action=logs``.

        Sends one ``GET /devicelogs`` (operation ``getDeviceLogs``) with
        ``serviceIds=config`` and ``actions=logs``, then follows
        ``x-next-page-url`` until it is absent. ``limit`` is forwarded on
        the first request only; later pages use the server URL as-is.

        Args:
            start_millis: Start of the search window. Passed through to
                ``startMillis`` (see :meth:`list_device`).
            imeis: One IMEI (or a sequence). Mutually exclusive with
                ``device_ids``.
            device_ids: One device UUID (or a sequence). Mutually exclusive
                with ``imeis``.
            end_millis: End of the search window; defaults to now on the server.
            limit: Maximum logs for the first request (server default 1000,
                max 100000).

        Returns:
            Config log rows in API order. These rows are not deduped.

        Raises:
            ValueError: If neither or both of ``imeis`` and ``device_ids``
                are provided.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._collect_device_logs(
            start_millis=start_millis,
            imeis=imeis,
            device_ids=device_ids,
            service_ids=(DeviceLogQueries.CONFIG_SERVICE,),
            actions=(DeviceLogQueries.LOGS_ACTION,),
            end_millis=end_millis,
            limit=limit,
        )

    def get_reports(
        self,
        *,
        start_millis: int,
        imeis: Optional[StrList] = None,
        device_ids: Optional[StrList] = None,
        end_millis: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[DeviceLog]:
        """Return telemetry and connection-send reports, deduped on ``(ts, rpt)``.

        Hypothesis: ``serviceIds`` and ``actions`` are ANDed, so the
        predicate ``(service=tel) OR (service=conn AND action in
        [new-sent, retry-sent])`` is two ``GET /devicelogs`` calls:

        * ``serviceIds=tel`` (no ``actions`` filter)
        * ``serviceIds=conn`` and ``actions=new-sent&actions=retry-sent``

        Pages are followed on each call. Rows are concatenated with every
        ``tel`` row before every ``conn`` row, then passed to
        :meth:`posiverse.device_logs.ReportIdentity.dedupe`.

        When two rows share ``(ts, rpt)`` and differ elsewhere, the earlier
        row is kept. A ``tel`` row therefore wins over a ``conn``
        ``new-sent`` or ``retry-sent`` row of the same report. Within one
        response, API order is preserved.

        ``ts`` and ``rpt`` are not schema fields. They are read from the
        ``request`` JSON object, then ``result``, then extra top-level
        fields. Rows without both keys are kept.

        Args:
            start_millis: Start of the search window (``startMillis``).
            imeis: One IMEI (or a sequence). Mutually exclusive with
                ``device_ids``.
            device_ids: One device UUID (or a sequence). Mutually exclusive
                with ``imeis``.
            end_millis: End of the search window; defaults to now on the server.
            limit: Maximum logs for the first request of each clause.

        Returns:
            Deduplicated report rows.

        Raises:
            ValueError: If neither or both of ``imeis`` and ``device_ids``
                are provided.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        tel_rows = self._collect_device_logs(
            start_millis=start_millis,
            imeis=imeis,
            device_ids=device_ids,
            service_ids=(DeviceLogQueries.TEL_SERVICE,),
            actions=None,
            end_millis=end_millis,
            limit=limit,
        )
        conn_rows = self._collect_device_logs(
            start_millis=start_millis,
            imeis=imeis,
            device_ids=device_ids,
            service_ids=(DeviceLogQueries.CONN_SERVICE,),
            actions=DeviceLogQueries.CONN_REPORT_ACTIONS,
            end_millis=end_millis,
            limit=limit,
        )
        return ReportIdentity.dedupe([*tel_rows, *conn_rows])

    def get_device_data(
        self,
        *,
        start_millis: int,
        imeis: Optional[StrList] = None,
        device_ids: Optional[StrList] = None,
        end_millis: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[DeviceLog]:
        """Return config logs and reports from one helper.

        This is the union of :meth:`get_logs` and :meth:`get_reports`:

        ``(service=config AND action=logs) OR (service=tel) OR
        (service=conn AND action in [new-sent, retry-sent])``.

        Hypothesis: that union is not one OpenAPI query. This method
        issues the same ``GET /devicelogs`` clauses as ``get_logs`` and
        ``get_reports`` (three requests, plus any further pages) and
        merges them. It is one public call, not one HTTP request.

        Merge order is config logs, then ``tel`` rows, then ``conn``
        rows. :meth:`posiverse.device_logs.ReportIdentity.dedupe` then
        runs on that sequence, so only rows that carry both ``ts`` and
        ``rpt`` collapse. A config log without that pair is kept even
        when reports are dropped. If a config log does carry the pair,
        it wins over a later report with the same pair.

        Args:
            start_millis: Start of the search window (``startMillis``).
            imeis: One IMEI (or a sequence). Mutually exclusive with
                ``device_ids``.
            device_ids: One device UUID (or a sequence). Mutually exclusive
                with ``imeis``.
            end_millis: End of the search window; defaults to now on the server.
            limit: Maximum logs for the first request of each clause.

        Returns:
            Config logs followed by deduplicated reports.

        Raises:
            ValueError: If neither or both of ``imeis`` and ``device_ids``
                are provided.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        logs = self.get_logs(
            start_millis=start_millis,
            imeis=imeis,
            device_ids=device_ids,
            end_millis=end_millis,
            limit=limit,
        )
        reports = self.get_reports(
            start_millis=start_millis,
            imeis=imeis,
            device_ids=device_ids,
            end_millis=end_millis,
            limit=limit,
        )
        return ReportIdentity.dedupe([*logs, *reports])

    def _collect_device_logs(
        self,
        *,
        start_millis: int,
        imeis: Optional[StrList],
        device_ids: Optional[StrList],
        service_ids: Sequence[str],
        actions: Optional[Sequence[str]],
        end_millis: Optional[int],
        limit: Optional[int],
    ) -> list[DeviceLog]:
        """Fetch every page of one conjunctive ``GET /devicelogs`` query.

        Args:
            start_millis: ``startMillis`` for the first request.
            imeis: IMEI filter. Mutually exclusive with ``device_ids``.
            device_ids: Device UUID filter. Mutually exclusive with ``imeis``.
            service_ids: ``serviceIds`` values for this clause.
            actions: ``actions`` values, or None to omit the parameter.
            end_millis: Optional ``endMillis``.
            limit: Optional ``limit`` for the first request.

        Returns:
            Rows from the first page and every followed ``x-next-page-url``.
            A repeated next URL stops the walk.

        Raises:
            ValueError: If the imei / device id XOR is not satisfied.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        items: list[DeviceLog] = []
        seen_next: set[str] = set()
        page = self.list_device(
            start_millis=start_millis,
            imeis=imeis,
            device_ids=device_ids,
            service_ids=list(service_ids),
            actions=list(actions) if actions is not None else None,
            end_millis=end_millis,
            limit=limit,
        )
        while True:
            items.extend(page.items)
            next_url = page.next_page_url
            if not next_url or next_url in seen_next:
                return items
            seen_next.add(next_url)
            nxt = self._client.follow_next_page(page, DeviceLog)
            if nxt is None:
                return items
            page = nxt

    def list_telemetry(
        self,
        *,
        start_millis: int,
        imeis: Optional[StrList] = None,
        end_millis: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[TelemetryLog]:
        """Search telemetry logs (operation ``getTelemetryLogs``).

        Args:
            start_millis: UTC millis since 1970-01-01 to start the search.
            imeis: Optional IMEI filter (string or sequence).
            end_millis: End of the search window; defaults to now on the server.
            limit: Maximum logs to return (server default 1000, max 100000).

        Returns:
            Paginated list of :class:`~posiverse.models.logs.TelemetryLog` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            "/telemetrylogs",
            item_model=TelemetryLog,
            params={
                "imeis": as_list(imeis),
                "startMillis": start_millis,
                "endMillis": end_millis,
                "limit": limit,
            },
        )

    def list_user(
        self,
        *,
        start_millis: int,
        user_ids: Optional[StrList] = None,
        service_ids: Optional[StrList] = None,
        actions: Optional[StrList] = None,
        end_millis: Optional[int] = None,
        and_terms: Optional[StrList] = None,
        or_terms: Optional[StrList] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[UserLog]:
        """Search user logs (operation ``getUserLogs``).

        Args:
            start_millis: UTC millis since 1970-01-01 to start the search.
            user_ids: User UUID filter (string or sequence).
            service_ids: Services to include (``api``, ``open_api``).
            actions: Action name filters.
            end_millis: End of the search window; defaults to now on the server.
            and_terms: Strings that must all appear in a log.
            or_terms: Strings of which at least one must appear in a log.
            limit: Maximum logs to return (server default 1000, max 100000).

        Returns:
            Paginated list of :class:`~posiverse.models.logs.UserLog` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            "/userlogs",
            item_model=UserLog,
            params={
                "userIds": as_list(user_ids),
                "serviceIds": as_list(service_ids),
                "actions": as_list(actions),
                "startMillis": start_millis,
                "endMillis": end_millis,
                "andTerms": as_list(and_terms),
                "orTerms": as_list(or_terms),
                "limit": limit,
            },
        )
