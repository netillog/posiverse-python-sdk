"""Shared helpers for live Posiverse integration tests.

Hard constraints:
    * Require ``POSIVERSE_BASE_URL`` (internal test OpenAPI); never production.
    * Never log, print, or commit ``POSIVERSE_API_KEY``.
    * Settings writes stay inside ``Release.json`` mask constraints and
      restore prior values when practical.
    * Avoid irreversible deletes of tenants/users/devices.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from posiverse.config import PosiverseConfig
from tests.live_guard import LiveTestGuard

# Known disposable TEST device (IMEI + UUID) for targeted reads/writes.
KNOWN_TEST_IMEI = "016080001000367"
KNOWN_TEST_DEVICE_ID = "9d9ba6c1-5ea5-d1b8-b78d-9b367a03f4c4"

# Rate limit observed on TEST: max 2 requests per second per tenant.
MIN_REQUEST_INTERVAL_SEC = 0.75

# Fixture path for Release.json mask constraints (copied into the repo).
RELEASE_JSON_PATH = Path(__file__).resolve().parent / "fixtures" / "Release.json"

# Mask section keys that live settings writes may touch.
ALLOWED_SETTINGS_MASK_KEYS = frozenset(
    {
        "ver",
        "config",
        "analytics",
        "telemetry",
        "ota",
        "motion",
        "vehicle",
        "driverBehavior",
        "driverId",
        "bluetooth",
    }
)


def live_integration_enabled() -> bool:
    """Return True when live integration tests should run.

    Returns:
        True if ``POSIVERSE_LIVE_INTEGRATION=1`` (preferred) or the older
        ``POSIVERSE_LIVE_SMOKE=1`` gate is set.
    """
    return LiveTestGuard.integration_enabled()


def assert_not_production_base_url(base_url: str) -> str:
    """Abort if ``base_url`` is the production OpenAPI host.

    Args:
        base_url: Client base URL under inspection.

    Returns:
        Normalized https URL.

    Raises:
        RuntimeError: If the URL points at production.
        ValueError: If the URL is not https.
    """
    return LiveTestGuard.assert_not_production(base_url)


def scrub_secrets(text: str) -> str:
    """Replace API key material in ``text`` with a redaction token.

    Args:
        text: Arbitrary log or exception text that might contain secrets.

    Returns:
        The same text with ``POSIVERSE_API_KEY`` value redacted when set.
    """
    key = os.environ.get(PosiverseConfig.API_KEY_ENV) or ""
    scrubbed = PosiverseConfig.redact_text(text, key)
    # Also scrub common header forms in case httpx dumps headers.
    scrubbed = re.sub(
        r"(posiverse-auth-key[\"'=\s:]+)[^\s\"']+",
        rf"\1{PosiverseConfig.REDACTED}",
        scrubbed,
        flags=re.IGNORECASE,
    )
    return scrubbed


def load_release_mask(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the Release.json settings mask used to constrain writes.

    Args:
        path: Optional override path. Defaults to the repo fixture copy.

    Returns:
        The ``mask`` object from Release.json.

    Raises:
        FileNotFoundError: If the fixture file is missing.
        KeyError: If the JSON lacks a ``mask`` key.
    """
    target = path or RELEASE_JSON_PATH
    with target.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["mask"]


def field_constraints(mask: Mapping[str, Any], section: str, field: str) -> Dict[str, Any]:
    """Return type/min/max/options/default metadata for a mask field.

    Args:
        mask: Release.json ``mask`` mapping.
        section: Top-level mask section (for example ``bluetooth``).
        field: Field name inside the section (for example ``scan``).

    Returns:
        Constraint dict for the field (may be empty if undocumented).

    Raises:
        KeyError: If ``section`` is not in the mask.
    """
    section_obj = mask[section]
    if not isinstance(section_obj, Mapping):
        return {}
    field_obj = section_obj.get(field, {})
    return dict(field_obj) if isinstance(field_obj, Mapping) else {}


def pick_alternate_int(current: Optional[int], constraints: Mapping[str, Any]) -> int:
    """Choose a different in-range integer for a reversible settings write.

    Args:
        current: Current field value (may be None).
        constraints: Field constraints from :func:`field_constraints`.

    Returns:
        An integer within min/max (or options) that differs from ``current``
        when possible.

    Raises:
        ValueError: If no valid alternate value can be derived.
    """
    options = constraints.get("options")
    if isinstance(options, list) and options:
        values = [opt.get("value") for opt in options if isinstance(opt, Mapping)]
        values = [int(v) for v in values if isinstance(v, (int, float))]
        for value in values:
            if value != current:
                return value
        if values:
            return values[0]

    minimum = constraints.get("min")
    maximum = constraints.get("max")
    default = constraints.get("default")
    if minimum is None and default is not None:
        minimum = default
    if maximum is None and default is not None:
        maximum = default
    if minimum is None or maximum is None:
        raise ValueError(f"Cannot pick alternate int without min/max: {constraints}")

    lo = int(minimum)
    hi = int(maximum)
    if current is None:
        return int(default) if isinstance(default, (int, float)) else lo
    cur = int(current)
    if cur < hi:
        return min(cur + 1, hi)
    if cur > lo:
        return max(cur - 1, lo)
    return cur



def call_with_retry(throttle: "RequestThrottle", fn, *, retries: int = 5):
    """Invoke ``fn`` with throttle waits and 429 retries.

    Args:
        throttle: Shared :class:`RequestThrottle`.
        fn: Zero-arg callable performing one API call.
        retries: Maximum attempts after the first try.

    Returns:
        The return value of ``fn``.

    Raises:
        Exception: Re-raises the last error when retries are exhausted.
    """
    from posiverse.errors import RateLimitError

    last_exc: Optional[Exception] = None
    attempts = retries + 1
    for attempt in range(attempts):
        throttle.wait()
        try:
            return fn()
        except RateLimitError as exc:
            last_exc = exc
            # Extra backoff beyond the normal throttle interval.
            time.sleep(0.75 * (attempt + 1))
    assert last_exc is not None
    raise last_exc


class RequestThrottle:
    """Simple client-side throttle for the TEST API 2 req/s limit.

    Args:
        min_interval: Minimum seconds between successive ``wait`` calls.
    """

    def __init__(self, min_interval: float = MIN_REQUEST_INTERVAL_SEC) -> None:
        self._min_interval = min_interval
        self._last: float = 0.0

    def wait(self) -> None:
        """Block until the minimum interval since the last call has elapsed."""
        now = time.monotonic()
        elapsed = now - self._last
        if self._last and elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last = time.monotonic()


def nested_get(data: Optional[Mapping[str, Any]], *keys: str) -> Any:
    """Read a nested mapping value, returning None when a key is missing.

    Args:
        data: Root mapping (or None).
        *keys: Nested key path.

    Returns:
        The value at the path, or None.
    """
    cur: Any = data
    for key in keys:
        if not isinstance(cur, Mapping) or key not in cur:
            return None
        cur = cur[key]
    return cur


def settings_section_dict(settings_obj: Any, section: str) -> Dict[str, Any]:
    """Extract a settings section as a plain dict from a Settings model.

    Args:
        settings_obj: A Settings pydantic model (or similar) with ``data``.
        section: Section name under ``data`` (for example ``bluetooth``).

    Returns:
        A plain dict of the section fields (empty if absent).
    """
    data = getattr(settings_obj, "data", None)
    if data is None:
        return {}
    section_obj = getattr(data, section, None)
    if section_obj is None:
        # Extra / raw mapping fallback.
        if isinstance(data, Mapping):
            raw = data.get(section) or {}
            return dict(raw) if isinstance(raw, Mapping) else {}
        extra = getattr(data, "__pydantic_extra__", None) or {}
        raw = extra.get(section) if isinstance(extra, Mapping) else None
        return dict(raw) if isinstance(raw, Mapping) else {}
    if hasattr(section_obj, "model_dump"):
        return section_obj.model_dump(mode="json", exclude_none=True)
    if isinstance(section_obj, Mapping):
        return dict(section_obj)
    return {}
