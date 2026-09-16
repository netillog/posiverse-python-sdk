"""Virtual console output line schema (OpenAPI ConsoleLine).

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class ConsoleLine(PosiverseModel):
    """A command that can be queued against a device and will get executed when device is connected to network"""

    date: Optional[int] = Field(
        None, description="Date the device printed console line in UTC seconds since 1970-01-01"
    )
    idx: Optional[int] = Field(
        None, description="Unique integer for each command.  Incremented by 1 for each new line."
    )
    data: Optional[str] = Field(None, description="A line of console text")
