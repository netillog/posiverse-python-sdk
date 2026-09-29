"""Live shape probe for the checked-in OpenAPI (TEST API only).

Records wire types and endpoint outcomes for the recommended-updates note.
Does not print API keys or response bodies. Failures of individual calls are
stored in the observation file; the dedicated per-tag tests still assert
success for the main reads.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import pytest

from posiverse.errors import APIError
from posiverse.models import Device
from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live

OBSERVATION_PATH = Path("/tmp/posiverse-live-observations.json")


def _kind(value: Any) -> str:
    """Return a coarse JSON kind name for ``value``."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _time_scale(value: Any) -> Optional[str]:
    """Classify an epoch-like integer without recording the raw timestamp."""
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    magnitude = abs(value)
    if magnitude == 0:
        return "zero"
    if magnitude < 10**11:
        return "seconds-scale"
    if magnitude < 10**14:
        return "millis-scale"
    if magnitude < 10**17:
        return "micros-scale"
    return "larger-than-micros"


def _field_kinds(item: Any) -> dict:
    """Map field names to kinds and time scales. Values are not copied."""
    if not isinstance(item, dict):
        return {"_body": _kind(item)}
    kinds = {}
    for key, value in item.items():
        entry = {"kind": _kind(value)}
        scale = _time_scale(value)
        if scale is not None and ("date" in key.lower() or key.lower().endswith("millis")):
            entry["time_scale"] = scale
        if key in {"date", "serverDate", "checkinDate", "synchDate"}:
            entry["time_scale"] = scale
        kinds[key] = entry
    return kinds


def _call(api, fn):  # noqa: ANN001
    """Run ``fn`` and return ``{"ok": True, ...}`` or a scrubbed error."""
    try:
        value = api.call_with_retry(fn)
    except APIError as exc:
        return {
            "ok": False,
            "status": exc.status_code,
            "message": scrub_secrets(str(exc))[:400],
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": None, "message": scrub_secrets(repr(exc))[:400]}
    return {"ok": True, "value": value}


def _page_template(url: Optional[str]) -> Optional[str]:
    """Reduce a next-page URL to a path template."""
    if not url:
        return None
    path = urlparse(url).path or url.split("?", 1)[0]
    if path.startswith("/pages/"):
        return "/pages/{pageId}"
    return path


def test_record_live_spec_observations(api, known_device_id, known_imei, discovered_ids):
    """Sample TEST responses and write field kinds for the spec note.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID.
        known_imei: Known TEST device IMEI.
        discovered_ids: Session-scoped discovered resource IDs.
    """
    start = int(time.time() * 1000) - (14 * 24 * 60 * 60 * 1000)
    observations: dict = {}

    device = _call(api, lambda: api.devices.get(known_device_id))
    if device["ok"]:
        dumped = device["value"].model_dump(exclude_unset=True)
        observations["device_get"] = {
            "ok": True,
            "present": sorted(dumped),
            "extra": sorted((device["value"].model_extra or {})),
            "vcm_kinds": {
                name: _kind(dumped.get(name))
                for name in ("isVcmStatic", "vcmProtocolId", "vcmProtocolId2", "vcmVehicleId")
                if name in dumped
            },
        }
    else:
        observations["device_get"] = {k: v for k, v in device.items() if k != "value"}

    user_id = discovered_ids.get("user_id")
    if user_id:
        user = _call(api, lambda: api.users.get(user_id))
        if user["ok"]:
            dumped = user["value"].model_dump(exclude_unset=True)
            observations["user_get"] = {
                "ok": True,
                "present": sorted(dumped),
                "extra": sorted((user["value"].model_extra or {})),
                "language_kind": _kind(dumped.get("language")) if "language" in dumped else None,
            }
        else:
            observations["user_get"] = {k: v for k, v in user.items() if k != "value"}
    else:
        observations["user_get"] = {"ok": False, "message": "no user id discovered"}

    synched = _call(api, lambda: api.devices.get_settings_synched(known_device_id))
    if synched["ok"]:
        dumped = synched["value"].model_dump(exclude_unset=True)
        observations["settings_synched"] = {
            "ok": True,
            "present": sorted(dumped),
            "extra": sorted((synched["value"].model_extra or {})),
            "errors_kind": _kind(dumped.get("errors")) if "errors" in dumped else None,
            "ver_present": "ver" in dumped,
        }
    else:
        observations["settings_synched"] = {k: v for k, v in synched.items() if k != "value"}

    logs = _call(
        api,
        lambda: api.request_json(
            "GET",
            "/devicelogs",
            params={"deviceIds": [known_device_id], "startMillis": start, "limit": 1},
        ),
    )
    if logs["ok"] and isinstance(logs["value"], list):
        observations["device_logs"] = {
            "ok": True,
            "count": len(logs["value"]),
            "item": _field_kinds(logs["value"][0]) if logs["value"] else None,
        }
    else:
        observations["device_logs"] = {k: v for k, v in logs.items() if k != "value"}

    no_identity = _call(
        api,
        lambda: api.request_json(
            "GET",
            "/devicelogs",
            params={"startMillis": start, "limit": 1},
        ),
    )
    observations["device_logs_no_identity"] = {
        k: v for k, v in no_identity.items() if k != "value"
    }
    if no_identity["ok"]:
        observations["device_logs_no_identity"]["count"] = (
            len(no_identity["value"]) if isinstance(no_identity["value"], list) else None
        )

    omitted_start = _call(
        api,
        lambda: api.request_json(
            "GET",
            "/devicelogs",
            params={"deviceIds": [known_device_id], "limit": 1},
        ),
    )
    observations["device_logs_omitted_start"] = {
        k: v for k, v in omitted_start.items() if k != "value"
    }

    telemetry = _call(
        api,
        lambda: api.request_json(
            "GET",
            "/telemetrylogs",
            params={"imeis": [known_imei], "startMillis": start, "limit": 1},
        ),
    )
    if telemetry["ok"] and isinstance(telemetry["value"], list):
        observations["telemetry_logs"] = {
            "ok": True,
            "count": len(telemetry["value"]),
            "item": _field_kinds(telemetry["value"][0]) if telemetry["value"] else None,
        }
    else:
        observations["telemetry_logs"] = {k: v for k, v in telemetry.items() if k != "value"}

    if user_id:
        user_logs = _call(
            api,
            lambda: api.request_json(
                "GET",
                "/userlogs",
                params={"userIds": [user_id], "startMillis": start, "limit": 1},
            ),
        )
        if user_logs["ok"] and isinstance(user_logs["value"], list):
            observations["user_logs"] = {
                "ok": True,
                "count": len(user_logs["value"]),
                "item": _field_kinds(user_logs["value"][0]) if user_logs["value"] else None,
            }
        else:
            observations["user_logs"] = {k: v for k, v in user_logs.items() if k != "value"}

    console = _call(
        api,
        lambda: api.request_json(
            "GET",
            f"/virtualconsole/{known_device_id}/0/0",
        ),
    )
    if console["ok"] and isinstance(console["value"], list):
        observations["console_new_path"] = {
            "ok": True,
            "count": len(console["value"]),
            "item": _field_kinds(console["value"][0]) if console["value"] else None,
        }
    else:
        observations["console_new_path"] = {k: v for k, v in console.items() if k != "value"}

    old_console = _call(
        api,
        lambda: api.request_json(
            "GET",
            f"/virtualconsole/{known_device_id}",
            params={"lastDate": 0},
        ),
    )
    observations["console_old_query_path"] = {
        k: v for k, v in old_console.items() if k != "value"
    }
    if old_console["ok"] and isinstance(old_console["value"], list):
        observations["console_old_query_path"]["count"] = len(old_console["value"])

    tag_id = discovered_ids.get("tag_id")
    if tag_id:
        tagged = _call(api, lambda: api.devices.list(tag_id=tag_id))
        if tagged["ok"]:
            observations["devices_by_tag"] = {
                "ok": True,
                "count": len(tagged["value"].items),
                "next": _page_template(tagged["value"].next_page_url),
            }
        else:
            observations["devices_by_tag"] = {k: v for k, v in tagged.items() if k != "value"}
    else:
        observations["devices_by_tag"] = {"ok": False, "message": "no tag id discovered"}

    listed = _call(api, lambda: api.devices.list())
    if listed["ok"]:
        next_url = listed["value"].next_page_url
        observations["devices_list_page"] = {
            "ok": True,
            "count": len(listed["value"].items),
            "next": _page_template(next_url),
        }
        if next_url and (
            "/pages/" in next_url
            or next_url.rstrip("/").split("/")[-2:-1] == ["pages"]
        ):
            page_id = next_url.rstrip("/").split("/")[-1].split("?")[0]
            item_model = type(listed["value"].items[0]) if listed["value"].items else Device
            followed = _call(
                api,
                lambda: api.pages.get(page_id, item_model=item_model),
            )
            observations["pages_get"] = {k: v for k, v in followed.items() if k != "value"}
            if followed["ok"]:
                observations["pages_get"]["count"] = len(followed["value"].items)
        elif next_url:
            observations["pages_get"] = {
                "ok": False,
                "message": "x-next-page-url was not a /pages/{pageId} path",
                "next": _page_template(next_url),
            }
        else:
            observations["pages_get"] = {"ok": False, "message": "no next page header"}
    else:
        observations["devices_list_page"] = {k: v for k, v in listed.items() if k != "value"}

    OBSERVATION_PATH.write_text(json.dumps(observations, indent=2, sort_keys=True), encoding="utf-8")
    assert observations
