"""Product record schema.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Product(PosiverseModel):
    """A product is a class of devices that share the same hardware"""

    id: Optional[str] = Field(None, description="Unique UUID for product")
    name: Optional[str] = Field(None, description="A short name for product")
    description: Optional[str] = Field(None, description="Notes about the product")
    modifiedDate: Optional[int] = Field(
        None, description="Date product was last modified, in UTC millis since 1970-01-01"
    )
    createdDate: Optional[int] = Field(
        None, description="Date product was created, in UTC millis since 1970-01-01"
    )
