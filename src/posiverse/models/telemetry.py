"""Pydantic models for Posiverse OpenAPI schemas.

Generated to match OpenAPI v1.1.1 component schemas. Field names preserve
API camelCase via population by field name (no aliasing required).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PosiverseModel(BaseModel):
    """Base model allowing extra fields from future API additions."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class TelemetryLog(PosiverseModel):
    """A log record class that contains data from telemetry log request."""
    imei: Optional[str] = Field(None, description="The IMEI of the device")
    date: Optional[int] = Field(None, description="The date the log was created on device")
    serverDate: Optional[int] = Field(None, description="The date the log was processed on server")
    json_: Optional[str] = Field(
        None,
        alias="json",
        description="Raw JSON data associated with Log",
    )
