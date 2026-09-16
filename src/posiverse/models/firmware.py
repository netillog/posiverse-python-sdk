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


class Firmware(PosiverseModel):
    """A data record class that contains firmware data."""
    id: Optional[str] = Field(None, description="UUID of firmware")
    productId: Optional[str] = Field(None, description="UUID of product associated with firmware")
    type: Optional[str] = Field(None, description="The type of the firmware, one of \"main\", \"power\", \"watchdog\", \"vcm\", \"modem\", \"bluetooth\", \"cell\", \"camera\", \"wifi\",\"nfc\"")
    version: Optional[str] = Field(None, description="The version of the firmware")
    createdDate: Optional[int] = Field(None, description="Date firmware was uploaded to Posiverse, in UTC millis since 1970-01-01")
