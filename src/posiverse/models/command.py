"""Queued device command schema (OpenAPI Command).

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Command(PosiverseModel):
    """A command that can be queued against a device and will get executed when device is connected to network"""

    id: Optional[str] = Field(None, description="Unique UUID for command")
    deviceId: Optional[str] = Field(None, description="Parent device UUID")
    command: Optional[str] = Field(None, description="Actual command to execute on device")
    createdById: Optional[str] = Field(None, description="User who created the command")
    createdDate: Optional[int] = Field(
        None, description="Date the command was created, in UTC millis since 1970-01-01"
    )
