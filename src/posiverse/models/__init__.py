"""Typed Pydantic models generated from Posiverse OpenAPI v1.1.1 schemas.

Re-exported here so callers can ``from posiverse.models import Device``.
"""

from posiverse.models.base import PosiverseModel
from posiverse.models.command import Command
from posiverse.models.console import ConsoleLine
from posiverse.models.device import Device, DevicePut
from posiverse.models.error import Error
from posiverse.models.firmware import Firmware
from posiverse.models.group import Group, GroupPut
from posiverse.models.logs import DeviceLog, ServerLog, TelemetryLog, UserLog
from posiverse.models.product import Product
from posiverse.models.properties import Properties, PropertiesData
from posiverse.models.scratchpad import Scratchpad
from posiverse.models.settings import (
    Settings,
    SettingsAnalytics,
    SettingsBluetooth,
    SettingsConfig,
    SettingsData,
    SettingsDriverBehaviour,
    SettingsExtTemp,
    SettingsMotion,
    SettingsOta,
    SettingsPut,
    SettingsSynched,
    SettingsTelemetry,
)
from posiverse.models.tag import Tag, TagMap, TagMapPut, TagPut
from posiverse.models.tenant import Tenant, TenantPut
from posiverse.models.user import User, UserPut

__all__ = [
    "PosiverseModel",
    "Error",
    "Command",
    "ConsoleLine",
    "SettingsExtTemp",
    "SettingsMotion",
    "SettingsOta",
    "SettingsTelemetry",
    "SettingsData",
    "SettingsDriverBehaviour",
    "SettingsConfig",
    "SettingsBluetooth",
    "SettingsAnalytics",
    "SettingsSynched",
    "Settings",
    "SettingsPut",
    "User",
    "UserPut",
    "UserLog",
    "TelemetryLog",
    "DeviceLog",
    "ServerLog",
    "Scratchpad",
    "Device",
    "DevicePut",
    "Properties",
    "PropertiesData",
    "Firmware",
    "Group",
    "GroupPut",
    "Product",
    "Tenant",
    "TenantPut",
    "Tag",
    "TagMap",
    "TagPut",
    "TagMapPut",
]
