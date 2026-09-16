"""Tag and TagMap records plus TagPut / TagMapPut request bodies.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Tag(PosiverseModel):
    """Tag is a meta data name that can be associated with an number of Device/User/Groups. Tags are used to orgainize data by associating mappings between objects."""

    id: Optional[str] = Field(None)
    tenantId: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    modifiedDate: Optional[int] = Field(None)
    createdDate: Optional[int] = Field(None)


class TagMap(PosiverseModel):
    """TagMap describes the association betwen a Tag and one of Device/User/Group"""

    tagId: Optional[str] = Field(None)
    ownerId: Optional[str] = Field(None)
    value: Optional[str] = Field(None)
    modifiedDate: Optional[int] = Field(None)
    createdDate: Optional[int] = Field(None)


class TagPut(PosiverseModel):
    """Object that contains field name which is only data that can be changed on Tag"""

    name: str = Field(...)


class TagMapPut(PosiverseModel):
    """Object that contains the field value with is only data that can be changed on TagMap"""

    value: str = Field(..., description="The value associated with a specific TagMap")
