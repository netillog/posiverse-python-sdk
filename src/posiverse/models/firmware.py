"""Firmware record schema.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Firmware(PosiverseModel):
    """A data record class that contains firmware data."""

    id: Optional[str] = Field(None, description="UUID of firmware")
    productId: Optional[str] = Field(None, description="UUID of product associated with firmware")
    type: Optional[str] = Field(
        None,
        description='The type of the firmware, one of "main", "power", "watchdog", "vcm", "modem", "bluetooth", "cell", "camera", "wifi","nfc"',
    )
    version: Optional[str] = Field(None, description="The version of the firmware")
    createdDate: Optional[int] = Field(
        None, description="Date firmware was uploaded to Posiverse, in UTC millis since 1970-01-01"
    )
