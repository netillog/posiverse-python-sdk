"""Device/group settings schemas, including nested sections and PUT body.

Field names match OpenAPI camelCase. Nested $ref types are imported
from sibling model modules. Extra API fields are preserved.
"""

from __future__ import annotations

from typing import Any, Optional, Union

from pydantic import Field

from posiverse.models.base import PosiverseModel


class SettingsExtTemp(PosiverseModel):
    """External temperature collection and reporting settings."""

    always: Optional[bool] = Field(None)
    rptInterval: Optional[int] = Field(None)
    collectInterval: Optional[int] = Field(None)


class SettingsMotion(PosiverseModel):
    """Motion / stop-detection settings for a device."""

    stopInterval: Optional[int] = Field(None)
    recheckTmSecs: Optional[int] = Field(None)
    telemInterval: Optional[int] = Field(None)
    interimStopInt: Optional[int] = Field(None)
    stopAccelWupThresh: Optional[int] = Field(None)


class SettingsOta(PosiverseModel):
    """Target firmware versions for over-the-air updates."""

    mainVer: Optional[str] = Field(None)
    modemVer: Optional[str] = Field(None)
    bluetoothVer: Optional[str] = Field(None)


class SettingsTelemetry(PosiverseModel):
    """Telemetry / MQTT reporting settings."""

    topic: Optional[str] = Field(None)
    feature: Optional[int] = Field(None)
    mqttUrl: Optional[str] = Field(None)
    rootCAUrl: Optional[str] = Field(None)
    reportList: Optional[str] = Field(None)
    provisionUrl: Optional[str] = Field(None)


class SettingsData(PosiverseModel):
    """Nested settings payload stored on a device or group."""

    ver: Optional[int] = Field(None)
    config: Optional[SettingsConfig] = Field(None)
    telemetry: Optional[SettingsTelemetry] = Field(None)
    ota: Optional[SettingsOta] = Field(None)
    motion: Optional[SettingsMotion] = Field(None)
    extTemp: Optional[SettingsExtTemp] = Field(None)
    analytics: Optional[SettingsAnalytics] = Field(None)
    bluetooth: Optional[SettingsBluetooth] = Field(None)
    driverBehavior: Optional[SettingsDriverBehaviour] = Field(None)


class SettingsDriverBehaviour(PosiverseModel):
    """Driver-behaviour scoring settings."""

    lightImp: Optional[int] = Field(None)


class SettingsConfig(PosiverseModel):
    """General device configuration settings (feature flags, interval)."""

    feature: Optional[int] = Field(None)
    interval: Optional[int] = Field(None)
    reportList: Optional[str] = Field(None)


class SettingsBluetooth(PosiverseModel):
    """Bluetooth scan and filter settings."""

    scan: Optional[int] = Field(None)
    macFilter: Optional[str] = Field(None)
    nameFilter: Optional[str] = Field(None)
    beaconFilter: Optional[str] = Field(None)
    moveInterval: Optional[int] = Field(None)
    stopInterval: Optional[int] = Field(None)


class SettingsAnalytics(PosiverseModel):
    """On-device analytics feature and interval settings."""

    feature: Optional[int] = Field(None)
    interval: Optional[int] = Field(None)


class SettingsSynched(PosiverseModel):
    """The actual settings on a device"""

    version: Optional[int] = Field(
        None, description="The version of the settings that have been synched"
    )
    # Live API currently returns ``ver`` (OpenAPI documents ``version``).
    ver: Optional[int] = Field(
        None, description="Live-API alias for the synched settings version"
    )
    data: Optional[SettingsData] = Field(
        None,
        description="The actual settings synched from device.  There may be a difference between Settings specified for a device and the SettingsSynched if the device has not synched with Posiverse since new Settings were specified.",
    )
    # OpenAPI types this as string; live TEST returns an object (often {}).
    errors: Optional[Union[str, dict, list, Any]] = Field(None)
    synchDate: Optional[int] = Field(
        None,
        description="Date the SettingsSynched were last synchronized with device, in UTC millis since 1970-01-01",
    )


class Settings(PosiverseModel):
    """The expected settings data for a device"""

    ver: Optional[int] = Field(None, description="Current settings version")
    data: Optional[SettingsData] = Field(
        None,
        description="Actual settings specified for a device,  The contents of the SettingsData will vary depending on actual device type and configuration",
    )
    modifiedDate: Optional[int] = Field(
        None, description="Date the Settings were last modified, in UTC millis since 1970-01-01"
    )


class SettingsPut(PosiverseModel):
    """The data record containing fields that can be modified on a settings. A description of Settings fields is available by clicking [here](https://www.positioninguniversal.com)"""

    config: Optional[SettingsConfig] = Field(None)
    telemetry: Optional[SettingsTelemetry] = Field(None)
    motion: Optional[SettingsMotion] = Field(None)
    extTemp: Optional[SettingsExtTemp] = Field(None)
    analytics: Optional[SettingsAnalytics] = Field(None)
    bluetooth: Optional[SettingsBluetooth] = Field(None)
    driverBehavior: Optional[SettingsDriverBehaviour] = Field(None)
