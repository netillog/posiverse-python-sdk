"""Tenant record and mutable TenantPut schemas.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Tenant(PosiverseModel):
    """A tenant is a base record of a group of objects representing an entity. So all other objects belong to a single tenant like device, group, user etc..."""

    id: Optional[str] = Field(None, description="Unique UUID for tenant")
    name: Optional[str] = Field(None, description="A short name for tenant")
    description: Optional[str] = Field(None, description="Notes about the tenant")
    modifiedDate: Optional[int] = Field(
        None, description="Date tenant was last modified, in UTC millis since 1970-01-01"
    )
    createdDate: Optional[int] = Field(
        None, description="Date tenant was created, in UTC millis since 1970-01-01"
    )


class TenantPut(PosiverseModel):
    """The data record containing fields that can be modified on a tenant"""

    name: Optional[str] = Field(None, description="A short name for tenant")
    description: Optional[str] = Field(None, description="Notes about the tenant")
