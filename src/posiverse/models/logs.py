"""Device, telemetry, user, and server log record schemas.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class UserLog(PosiverseModel):
    """A log record class that contains data from user actions."""

    userId: Optional[str] = Field(None, description="The UUID of the user making the request")
    date: Optional[int] = Field(
        None,
        description="The date the log was processed on cloud backend, in UTC millis from 1970-01-01",
    )
    status: Optional[str] = Field(
        None,
        description='One of "200 Success", "304 Not Modified","400 Bad Request","401 Unauthenticated","403 Forbidden","404 Not Found","429 Too Many Requests","500 Internal Server Error","502 Bad Gateway"',
    )
    service: Optional[str] = Field(
        None,
        description='Will be "open_api" if user request came through this OpenApi system or "api" if the request came from Posiverse UI.',
    )
    action: Optional[str] = Field(None, description="A short name for the type of user request")
    databaseId: Optional[str] = Field(
        None,
        description="A UUID that groups all database changes taken by a specific user action.  For example: changing a group's settings will cause the settings database record for each device in the group to change.  Each of these database records will have the same databaseId that can be looked up with database log search.",
    )
    request: Optional[str] = Field(
        None, description="The incoming JSON object representing the user's request to the system"
    )
    result: Optional[str] = Field(
        None, description="The result of the request from the user in JSON"
    )
    logs: Optional[List[ServerLog]] = Field(
        None, description="Specific logs from the handling of the user action"
    )


class TelemetryLog(PosiverseModel):
    """A log record class that contains data from telemetry log request."""

    imei: Optional[str] = Field(None, description="The IMEI of the device")
    date: Optional[int] = Field(None, description="The date the log was created on device")
    serverDate: Optional[int] = Field(None, description="The date the log was processed on server")
    json_: Optional[str] = Field(
        None, alias="json", description="Raw JSON data associated with Log"
    )


class DeviceLog(PosiverseModel):
    """A data record class that contains information about a device log."""

    deviceId: Optional[str] = Field(None, description="UUID of device")
    date: Optional[int] = Field(
        None,
        description="The date the log was processed on cloud backend, in UTC millis from 1970-01-01",
    )
    status: Optional[str] = Field(
        None, description='One of "200 Success", "400 Bad Request","500 Internal Server Error"'
    )
    imei: Optional[str] = Field(
        None,
        description="IMEI of device, redundant with UUID but useful since most users work with IMEI to identify device",
    )
    service: Optional[str] = Field(
        None,
        description='Service represents the originating provider that created the log "config", "tel", "firmware", "ephemeris", "certs", "open_api", "api", "conn"',
    )
    action: Optional[str] = Field(
        None, description="A short name for the action that caused the log to be created"
    )
    databaseId: Optional[str] = Field(
        None,
        description="A UUID that groups all database changes taken by a specific device action.  For example: a device that changes its VIN will cause change in device properties and potentially the device's settings and device's field vcmVehicleLibVer.",
    )
    request: Optional[str] = Field(
        None, description="The incoming JSON object representing the request to the system"
    )
    result: Optional[str] = Field(None, description="The result of the request in JSON")
    logs: Optional[List[ServerLog]] = Field(
        None, description="Specific logs from the handling of the action"
    )


class ServerLog(PosiverseModel):
    """Each action processed on Posiverse cloud can generate information server logs. This is is an instance of a single log."""

    date: Optional[int] = Field(
        None, description="Date log was created in UTC millis since 1970-01-01"
    )
    level: Optional[str] = Field(
        None, description='A measure of log severity, one of "debug", "info", "warn", "error"'
    )
    msg: Optional[str] = Field(None, description="The actual log message")
