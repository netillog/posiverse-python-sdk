"""Error payload schema returned by Posiverse on failed requests.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Error(PosiverseModel):
    """Generic Error message returned from server, used as base class for all error responses"""

    code: int = Field(...)
    message: str = Field(...)
