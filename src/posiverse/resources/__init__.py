"""Resource namespaces for Posiverse OpenAPI tags."""

from posiverse.resources.commands import CommandsResource
from posiverse.resources.devices import DevicesResource
from posiverse.resources.firmwares import FirmwaresResource
from posiverse.resources.groups import GroupsResource
from posiverse.resources.logs import LogsResource
from posiverse.resources.products import ProductsResource
from posiverse.resources.settings import SettingsResource
from posiverse.resources.tagmaps import TagMapsResource
from posiverse.resources.tags import TagsResource
from posiverse.resources.tenants import TenantsResource
from posiverse.resources.users import UsersResource
from posiverse.resources.virtual_console import VirtualConsoleResource

__all__ = [
    "CommandsResource",
    "DevicesResource",
    "FirmwaresResource",
    "GroupsResource",
    "LogsResource",
    "ProductsResource",
    "SettingsResource",
    "TagMapsResource",
    "TagsResource",
    "TenantsResource",
    "UsersResource",
    "VirtualConsoleResource",
]
