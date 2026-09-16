"""Pagination helpers for Posiverse list endpoints.

Posiverse returns pagination metadata in response headers rather than the
JSON body. The OpenAPI documents four headers:

* ``x-total-count``: total objects matching the query (always returned)
* ``x-page-count``: objects in the current response (always returned)
* ``x-page-start``: zero-based offset of this page (always returned)
* ``x-next-page-url``: partial URL of the next page; prepend the client
  base URL. Absent when no further pages exist.
"""

from __future__ import annotations

from typing import Any, Generic, List, Mapping, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

# Canonical pagination header names from the OpenAPI specification.
HEADER_TOTAL_COUNT = "x-total-count"
HEADER_PAGE_COUNT = "x-page-count"
HEADER_PAGE_START = "x-page-start"
HEADER_NEXT_PAGE_URL = "x-next-page-url"


class PaginatedResponse(BaseModel, Generic[T]):
    """Container for a page of list results plus pagination headers.

    Attributes:
        items: Objects returned in the current page.
        total_count: Total number of matching objects (x-total-count).
        page_count: Number of objects in this response (x-page-count).
        page_start: Zero-based offset into the full result set (x-page-start).
        next_page_url: Partial URL for the next page (x-next-page-url), or None
            when no further pages exist. Prepend the client base URL to use it.
    """

    items: List[T] = Field(default_factory=list)
    total_count: Optional[int] = None
    page_count: Optional[int] = None
    page_start: Optional[int] = None
    next_page_url: Optional[str] = None

    @property
    def has_next_page(self) -> bool:
        """Return True when a next-page URL header was present."""
        return bool(self.next_page_url)

    def absolute_next_page_url(self, base_url: str) -> Optional[str]:
        """Build a requestable next-page URL from the partial header value.

        Args:
            base_url: Server URL used for the original request (no trailing
                path). The OpenAPI requires callers to prepend this value.

        Returns:
            An absolute URL, the original value if it is already absolute,
            or None when there is no next page.
        """
        if not self.next_page_url:
            return None
        next_url = self.next_page_url
        if next_url.startswith("http://") or next_url.startswith("https://"):
            return next_url
        return base_url.rstrip("/") + "/" + next_url.lstrip("/")


def parse_int_header(headers: Mapping[str, Any], name: str) -> Optional[int]:
    """Parse an integer pagination header, returning None if absent/invalid.

    Args:
        headers: Case-insensitive mapping of response headers.
        name: Header name to read.

    Returns:
        Parsed integer value, or None when missing or not an integer.
    """
    raw = headers.get(name) if hasattr(headers, "get") else None
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def pagination_from_headers(headers: Mapping[str, Any]) -> dict:
    """Extract pagination fields from an HTTP response header mapping.

    Args:
        headers: Response headers (for example ``httpx.Headers``, which is
            case-insensitive so ``x-total-count`` matches ``X-Total-Count``).

    Returns:
        Dict suitable for constructing :class:`PaginatedResponse` kwargs.
    """
    get = headers.get
    next_url = get(HEADER_NEXT_PAGE_URL)
    if next_url == "":
        next_url = None
    return {
        "total_count": parse_int_header(headers, HEADER_TOTAL_COUNT),
        "page_count": parse_int_header(headers, HEADER_PAGE_COUNT),
        "page_start": parse_int_header(headers, HEADER_PAGE_START),
        "next_page_url": next_url,
    }
