"""Group record and mutable GroupPut schemas.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Group(PosiverseModel):
    """A group is a collection of devices with similar settings"""

    id: Optional[str] = Field(None, description="Unique UUID for group")
    productId: Optional[str] = Field(None, description="UUID of product assciated with group")
    name: Optional[str] = Field(None, description="A short name for group")
    description: Optional[str] = Field(None, description="Notes about the group")
    modifiedDate: Optional[int] = Field(
        None, description="Date the group was last modified, in UTC millis since 1970-01-01"
    )
    createdDate: Optional[int] = Field(
        None, description="Date group was created, in UTC millis since 1970-01-01"
    )


class GroupPut(PosiverseModel):
    """The data record containing fields that can be modified on a group"""

    name: Optional[str] = Field(None, description="A short name for group")
    description: Optional[str] = Field(None, description="Notes about the group")
