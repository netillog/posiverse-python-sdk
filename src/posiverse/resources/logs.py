"""Logs resource — OpenAPI tag Logs.

Paths: GET ``/devicelogs``, GET ``/telemetrylogs``, GET ``/userlogs``.
"""

from __future__ import annotations

from typing import Optional, Sequence, Union

from posiverse._utils import as_list
from posiverse.models import DeviceLog, TelemetryLog, UserLog
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource

StrList = Union[str, Sequence[str]]


class LogsResource(BaseResource):
    """Query device, telemetry, and user activity logs."""

    def list_device(
        self,
        *,
        imeis: Optional[StrList] = None,
        device_ids: Optional[StrList] = None,
        database_ids: Optional[StrList] = None,
        service_ids: Optional[StrList] = None,
        actions: Optional[StrList] = None,
        min_log_level: Optional[str] = None,
        min_duration: Optional[int] = None,
        start_millis: Optional[int] = None,
        end_millis: Optional[int] = None,
        and_terms: Optional[StrList] = None,
        or_terms: Optional[StrList] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[DeviceLog]:
        """Search device logs (operation ``getDeviceLogs``).

        The OpenAPI marks both ``imeis`` and ``deviceIds`` optional. Their
        descriptions say only one of the two can be provided, so this method
        rejects a call that sets both. Omitting both is allowed and left to
        the server. ``startMillis`` is optional and defaults on the server to
        10 minutes ago. The documented window is the past 365 days and may
        not span more than 30 days. Values are UTC milliseconds.

        Args:
            imeis: One IMEI (or a sequence). Mutually exclusive with
                ``device_ids``. Max 1 IMEI per query.
            device_ids: One device UUID (or a sequence). Mutually exclusive
                with ``imeis``. Max 1 device id per query.
            database_ids: Database UUIDs to filter logs by (``databaseIds``).
            service_ids: Services to include (``config``, ``tel``,
                ``firmware``, ``ephemeris``, ``certs``, ``open_api``,
                ``api``, ``conn``).
            actions: Action name filters.
            min_log_level: Minimum log level (``debug``, ``info``, ``warn``,
                ``error``).
            min_duration: Minimum execution duration in milliseconds.
            start_millis: Start of the search window in UTC millis since
                1970-01-01. Server default is 10 minutes ago. Limited to the
                past 365 days.
            end_millis: End of the search window in UTC millis; defaults to
                now on the server. The query may not span more than 30 days.
            and_terms: Strings that must all appear in a log.
            or_terms: Strings of which at least one must appear in a log.
            limit: Maximum logs to return (server default 1000).

        Returns:
            Paginated list of :class:`~posiverse.models.logs.DeviceLog` objects.

        Raises:
            ValueError: If both ``imeis`` and ``device_ids`` are provided.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        imei_list = as_list(imeis)
        device_id_list = as_list(device_ids)
        if imei_list and device_id_list:
            raise ValueError("Provide at most one of imeis or device_ids")
        return self._client.request_paginated(
            "GET",
            "/devicelogs",
            item_model=DeviceLog,
            params={
                "imeis": imei_list,
                "deviceIds": device_id_list,
                "databaseIds": as_list(database_ids),
                "serviceIds": as_list(service_ids),
                "actions": as_list(actions),
                "minLogLevel": min_log_level,
                "minDuration": min_duration,
                "startMillis": start_millis,
                "endMillis": end_millis,
                "andTerms": as_list(and_terms),
                "orTerms": as_list(or_terms),
                "limit": limit,
            },
        )

    def list_telemetry(
        self,
        *,
        imeis: Optional[StrList] = None,
        start_millis: Optional[int] = None,
        end_millis: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[TelemetryLog]:
        """Search telemetry logs (operation ``getTelemetryLogs``).

        Args:
            imeis: Optional IMEI filter (string or sequence).
            start_millis: UTC millis since 1970-01-01 to start the search.
                Server default is 4 hours ago.
            end_millis: End of the search window in UTC millis; defaults to
                now on the server.
            limit: Maximum logs to return (server default 1000, max 5000).

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
        user_ids: Optional[StrList] = None,
        database_ids: Optional[StrList] = None,
        service_ids: Optional[StrList] = None,
        actions: Optional[StrList] = None,
        min_log_level: Optional[str] = None,
        min_duration: Optional[int] = None,
        start_millis: Optional[int] = None,
        end_millis: Optional[int] = None,
        and_terms: Optional[StrList] = None,
        or_terms: Optional[StrList] = None,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[UserLog]:
        """Search user logs (operation ``getUserLogs``).

        Args:
            user_ids: User UUID filter (string or sequence).
            database_ids: Database UUIDs to filter logs by (``databaseIds``).
            service_ids: Services to include (``api``, ``open_api``).
            actions: Action name filters.
            min_log_level: Minimum log level (``debug``, ``info``, ``warn``,
                ``error``).
            min_duration: Minimum execution duration in milliseconds.
            start_millis: UTC millis since 1970-01-01 to start the search.
                Server default is 10 minutes ago. Limited to the past 365
                days. The query may not span more than 30 days.
            end_millis: End of the search window in UTC millis; defaults to
                now on the server.
            and_terms: Strings that must all appear in a log.
            or_terms: Strings of which at least one must appear in a log.
            limit: Maximum logs to return (server default 1000).

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
                "databaseIds": as_list(database_ids),
                "serviceIds": as_list(service_ids),
                "actions": as_list(actions),
                "minLogLevel": min_log_level,
                "minDuration": min_duration,
                "startMillis": start_millis,
                "endMillis": end_millis,
                "andTerms": as_list(and_terms),
                "orTerms": as_list(or_terms),
                "limit": limit,
            },
        )
