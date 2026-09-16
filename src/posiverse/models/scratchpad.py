"""Device scratchpad backup-state schema.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Scratchpad(PosiverseModel):
    """The data stored on cloud be device to backup critical state information which is needed if flash memory gets completely wiped."""

    ver: Optional[int] = Field(
        None,
        description="The current version of the scratchpad,  increases by 1 each time device updates its scratchpad.",
    )
    totalFuel: Optional[int] = Field(None)
    featureCfg: Optional[int] = Field(None)
    engineHrsCalc: Optional[float] = Field(None)
    odometerOffset: Optional[int] = Field(None)
    engineHrsOffset: Optional[float] = Field(None)
    odometerAllowed: Optional[int] = Field(None)
    odometerDerived: Optional[int] = Field(None)
    gpsCalculatedOdo: Optional[int] = Field(None)
