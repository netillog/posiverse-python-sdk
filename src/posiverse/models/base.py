"""Shared Pydantic base for Posiverse OpenAPI component schemas.

Field names match the API's camelCase JSON (for example ``deviceId``)
so payloads round-trip without alias maps. Extra properties are kept so
newer API fields do not fail validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PosiverseModel(BaseModel):
    """Base model for all Posiverse request and response schemas.

    Attributes:
        model_config: Pydantic v2 config. Extra fields are allowed and
            both field names and aliases may be used when parsing.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)
