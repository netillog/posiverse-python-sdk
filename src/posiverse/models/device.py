"""Device record and mutable DevicePut schemas.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Optional, Union

from pydantic import Field

from posiverse.models.base import PosiverseModel
from posiverse.models.properties import PropertiesData
from posiverse.models.scratchpad import Scratchpad
from posiverse.models.settings import SettingsData


class Device(PosiverseModel):
    """A data record class that contains device data."""

    id: Optional[str] = Field(None, description="UUID of device")
    productId: Optional[str] = Field(None, description="UUID of product associated with device")
    groupId: Optional[str] = Field(None, description="UUID of group associated with device")
    name: Optional[str] = Field(None, description="A short name for device")
    description: Optional[str] = Field(
        None,
        description="Notes about device, only returned when full version of device is requested",
    )
    serial: Optional[str] = Field(
        None, description="The unique identifier for device printed on label attached to device"
    )
    externalDeviceId: Optional[str] = Field(None, description="An external Device ID")
    imei: Optional[str] = Field(None)
    iccid: Optional[str] = Field(None)
    imsi: Optional[str] = Field(None)
    checkinDate: Optional[int] = Field(
        None,
        description="Last date the device checked into Posiverse cloud, in UTC millis since 1970-01-01",
    )
    # Live TEST/PROD APIs may return int despite OpenAPI type:string; accept both.
    propertiesVer: Optional[Union[str, int]] = Field(
        None, description="The current version of the properties"
    )
    propertiesDate: Optional[int] = Field(
        None,
        description="Last date the device updated its properties, in UTC millis since 1970-01-01",
    )
    # Live TEST/PROD APIs may return int despite OpenAPI type:string; accept both.
    settingsVer: Optional[Union[str, int]] = Field(
        None, description="The current version of the settings"
    )
    settingsDate: Optional[int] = Field(
        None, description="Date expected settings where created, in UTC millis since 1970-01-01"
    )
    settingsSynchedDate: Optional[int] = Field(
        None, description="Last date device synched its settings, in UTC millis since 1970-01-01"
    )
    mainFwVer: Optional[str] = Field(
        None, description="Current reported version of Main firmware on device"
    )
    modemFwVer: Optional[str] = Field(
        None, description="Current reported version of Cellular modem firmware on device"
    )
    gpsFwVer: Optional[str] = Field(
        None, description="Current reported version of GPS module firmware on device"
    )
    bluetoothFwVer: Optional[str] = Field(
        None, description="Current reported version of GPS module firmware on device"
    )
    vcmFwVer: Optional[str] = Field(
        None, description="Current reported version of VCM module firmware on device"
    )
    scratchpad: Optional[Scratchpad] = Field(
        None,
        description="The latest scratchpad reported for a device, only returned when full version of device is requested",
    )
    properties: Optional[PropertiesData] = Field(
        None,
        description="The expected settings for a device, only returned when full version of device is requested",
    )
    settings: Optional[SettingsData] = Field(
        None,
        description="The expected settings for a device, only returned when full version of device is requested",
    )
    settingsSynched: Optional[SettingsData] = Field(
        None,
        description="The actual settings on the device, only returned when full version of device is requested",
    )
    modifiedDate: Optional[int] = Field(
        None, description="Date device was last modified, in UTC millis since 1970-01-01"
    )
    createdDate: Optional[int] = Field(
        None, description="Date device was originally created, in UTC millis since 1970-01-01"
    )


class DevicePut(PosiverseModel):
    """The data record containing fields that can be modified on a device"""

    groupId: Optional[str] = Field(None, description="UUID of group associated with device")
    name: Optional[str] = Field(None, description="A short name for device")
    description: Optional[str] = Field(None, description="Notes about device")
    externalDeviceId: Optional[str] = Field(
        None, description="An external device ID. This field is limited to 64 characters."
    )
