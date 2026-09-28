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
