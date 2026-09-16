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


class Tenant(PosiverseModel):
    """A tenant is a base record of a group of objects representing an entity.  So all other objects belong to a single tenant like device, group, user etc..."""
    id: Optional[str] = Field(None, description="Unique UUID for tenant")
    name: Optional[str] = Field(None, description="A short name for tenant")
    description: Optional[str] = Field(None, description="Notes about the tenant")
    modifiedDate: Optional[int] = Field(None, description="Date tenant was last modified, in UTC millis since 1970-01-01")
    createdDate: Optional[int] = Field(None, description="Date tenant was created, in UTC millis since 1970-01-01")

class TenantPut(PosiverseModel):
    """The data record containing fields that can be modified on a tenant"""
    name: Optional[str] = Field(None, description="A short name for tenant")
    description: Optional[str] = Field(None, description="Notes about the tenant")
