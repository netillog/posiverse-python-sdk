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


class Product(PosiverseModel):
    """A product is a class of devices that share the same hardware"""
    id: Optional[str] = Field(None, description="Unique UUID for product")
    name: Optional[str] = Field(None, description="A short name for product")
    description: Optional[str] = Field(None, description="Notes about the product")
    modifiedDate: Optional[int] = Field(None, description="Date product was last modified, in UTC millis since 1970-01-01")
    createdDate: Optional[int] = Field(None, description="Date product was created, in UTC millis since 1970-01-01")
