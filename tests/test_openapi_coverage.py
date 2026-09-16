"""Verify the SDK covers every OpenAPI operationId (no invented endpoints)."""

from __future__ import annotations

import json
from pathlib import Path

from posiverse import PosiverseClient

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = REPO_ROOT / "openapi" / "posiverse.openapi.json"

# operationId → (client attribute, method name) — must match OpenAPI v1.1.1.
OPERATION_MAP = {
    "getCommands": ("commands", "list"),
    "addCommand": ("commands", "add"),
    "deleteCommand": ("commands", "delete"),
    "getDevices": ("devices", "list"),
    "getDevice": ("devices", "get"),
    "modifyDevice": ("devices", "update"),
    "getFirmwares": ("firmwares", "list"),
    "getFirmware": ("firmwares", "get"),
    "getGroups": ("groups", "list"),
    "getGroup": ("groups", "get"),
    "modifyGroup": ("groups", "update"),
    "getProducts": ("products", "list"),
    "getProduct": ("products", "get"),
    "getProperties": ("devices", "get_properties"),
    "getScratchpad": ("devices", "get_scratchpad"),
    "getSettings": ("settings", "get"),
    "modifySettings": ("settings", "update"),
    "getSettingsSynched": ("devices", "get_settings_synched"),
    "getUsers": ("users", "list"),
    "getUser": ("users", "get"),
    "modifyUser": ("users", "update"),
    "getConsoleOutput": ("virtual_console", "get_output"),
    "addCommandToConsole": ("virtual_console", "send"),
    "getTenants": ("tenants", "list"),
    "getTenant": ("tenants", "get"),
    "modifyTenant": ("tenants", "update"),
    "getTags": ("tags", "list"),
    "addTag": ("tags", "create"),
    "getTag": ("tags", "get"),
    "modifyTag": ("tags", "update"),
    "deleteTag": ("tags", "delete"),
    "getTagMaps": ("tagmaps", "list"),
    "getTagMap": ("tagmaps", "get"),
    "modifyTagMap": ("tagmaps", "update"),
    "addTagMap": ("tagmaps", "create"),
    "deleteTagMap": ("tagmaps", "delete"),
    "getDeviceLogs": ("logs", "list_device"),
    "getTelemetryLogs": ("logs", "list_telemetry"),
    "getUserLogs": ("logs", "list_user"),
}


def _spec_operation_ids():
    spec = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
    ids = []
    for path_item in spec["paths"].values():
        for method, op in path_item.items():
            if not isinstance(op, dict):
                continue
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            oid = op.get("operationId")
            if oid:
                ids.append(oid)
    return ids


def test_openapi_file_is_v1_1_1():
    """The checked-in spec is the source of truth (Posiverse OpenAPI v1.1.1)."""
    spec = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
    assert spec["openapi"].startswith("3.0")
    assert spec["info"]["version"] == "v1.1.1"
    servers = {s["url"] for s in spec["servers"]}
    assert "https://openapi-test.posiverse.com" in servers
    assert "https://openapi-prod.posiverse.com" in servers
    scheme = spec["components"]["securitySchemes"]["bearerAuth"]
    assert scheme["type"] == "apiKey"
    assert scheme["name"] == "posiverse-auth-key"
    assert scheme["in"] == "header"


def test_every_operation_id_is_mapped(client: PosiverseClient):
    """Every OpenAPI operationId has a corresponding SDK method."""
    spec_ids = _spec_operation_ids()
    assert set(spec_ids) == set(OPERATION_MAP)
    for operation_id, (attr, method_name) in OPERATION_MAP.items():
        resource = getattr(client, attr)
        assert hasattr(resource, method_name), f"{operation_id} -> {attr}.{method_name}"
        assert callable(getattr(resource, method_name))


def test_required_tags_are_on_client(client: PosiverseClient):
    """Client exposes a namespace for each functional OpenAPI tag."""
    for name in (
        "commands",
        "devices",
        "firmwares",
        "groups",
        "logs",
        "products",
        "settings",
        "tagmaps",
        "tags",
        "tenants",
        "users",
        "virtual_console",
    ):
        assert hasattr(client, name)
