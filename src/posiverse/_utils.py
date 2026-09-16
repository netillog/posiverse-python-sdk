"""Small helpers for query parameters and JSON request bodies.

These keep resource modules focused on OpenAPI paths rather than
httpx/pydantic serialization details.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union

from pydantic import BaseModel


def drop_none(params: Optional[Mapping[str, Any]]) -> Optional[dict]:
    """Return a copy of ``params`` with ``None`` values removed.

    Args:
        params: Query or header mapping, or None.

    Returns:
        A dict containing only keys with non-None values, or None when
        the input is empty after filtering (so httpx omits ``params``).
    """
    if not params:
        return None
    cleaned = {key: value for key, value in params.items() if value is not None}
    return cleaned or None


def as_list(value: Optional[Union[str, Sequence[str]]]) -> Optional[list]:
    """Normalize a string or sequence into a list for array query params.

    OpenAPI array query parameters (for example ``imeis``, ``deviceIds``)
    accept repeated keys. Passing a single string is treated as one item.

    Args:
        value: A string, a sequence of strings, or None.

    Returns:
        A list of strings, or None when ``value`` is None.
    """
    if value is None:
        return None
    if isinstance(value, (str, bytes)):
        return [value]
    return list(value)


def dump_json_body(body: Any) -> Any:
    """Serialize a Pydantic model (or pass through a mapping) as JSON data.

    Uses ``by_alias=True`` so fields such as TelemetryLog ``json`` round-trip
    with their OpenAPI names. ``None`` fields are omitted.

    Args:
        body: A pydantic model, a dict, or None.

    Returns:
        A JSON-serializable mapping, or the original value when not a model.
    """
    if body is None:
        return None
    if isinstance(body, BaseModel):
        return body.model_dump(mode="json", exclude_none=True, by_alias=True)
    return body
