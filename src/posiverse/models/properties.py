"""Device properties envelope and PropertiesData schemas.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from posiverse.models.base import PosiverseModel


class Properties(PosiverseModel):
    """The configuration information present on the device, and solely controlled by the device, that is shared with the cloud."""

    ver: Optional[int] = Field(
        None,
        description="The current version of the properties,  increases by 1 each time device updates its properties.",
    )
    data: Optional[PropertiesData] = Field(None)
    modifiedDate: Optional[int] = Field(
        None,
        description="Date Settings were last modified, in UTC millis since 1970-01-01.  The Properties were created at the same time as the associated Device.",
    )


class PropertiesData(PosiverseModel):
    """''"""

    apn: Optional[str] = Field(None)
    ver: Optional[str] = Field(None)
    vin: Optional[str] = Field(None)
    imsi: Optional[str] = Field(None)
    btMac: Optional[str] = Field(None)
    gpsHw: Optional[str] = Field(None)
    iccid: Optional[str] = Field(None)
    bootVer: Optional[str] = Field(None)
    ecmOvrd: Optional[str] = Field(None)
    mainVer: Optional[str] = Field(None)
    vcmType: Optional[str] = Field(None)
    vcmProtocol: Optional[str] = Field(None)
    modemVer: Optional[str] = Field(None)
    vbusOvrd: Optional[str] = Field(None)
    cfgBitmask: Optional[str] = Field(None)
    productType: Optional[str] = Field(None)
    bluetoothVer: Optional[str] = Field(None)
    harshDriveOvrd: Optional[str] = Field(None)
    vehicleManufacturerInfo: Optional[str] = Field(None)
