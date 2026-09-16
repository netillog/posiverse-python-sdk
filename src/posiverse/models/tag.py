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


class Tag(PosiverseModel):
    """Tag is a meta data name that can be associated with an number of Device/User/Groups.  Tags are used to orgainize data by associating mappings between objects."""
    id: Optional[str] = None
    tenantId: Optional[str] = None
    name: Optional[str] = None
    modifiedDate: Optional[int] = None
    createdDate: Optional[int] = None

class TagPut(PosiverseModel):
    """Object that contains field name which is only data that can be changed on Tag"""
    name: str

class TagMap(PosiverseModel):
    """TagMap describes the association betwen a Tag and one of Device/User/Group"""
    tagId: Optional[str] = None
    ownerId: Optional[str] = None
    value: Optional[str] = None
    modifiedDate: Optional[int] = None
    createdDate: Optional[int] = None

class TagMapPut(PosiverseModel):
    """Object that contains the field value with is only data that can be changed on TagMap"""
    value: str = Field(..., description="The value associated with a specific TagMap")
