"""Pagination helpers for Posiverse list endpoints.

Posiverse returns pagination metadata in response headers rather than the
JSON body. See OpenAPI info.description for header semantics.
"""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

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


def parse_int_header(headers: dict, name: str) -> Optional[int]:
    """Parse an integer pagination header, returning None if absent/invalid.

    Args:
        headers: Case-insensitive mapping of response headers.
        name: Header name to read.

    Returns:
        Parsed integer value, or None when missing or not an integer.
    """
    raw = headers.get(name)
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def pagination_from_headers(headers: dict) -> dict:
    """Extract pagination fields from an HTTP response header mapping.

    Args:
        headers: Response headers (e.g. ``httpx.Headers``).

    Returns:
        Dict suitable for constructing :class:`PaginatedResponse` kwargs.
    """
    # httpx.Headers is case-insensitive; normalize via .get
    get = headers.get if hasattr(headers, "get") else lambda k: headers[k]
    return {
        "total_count": parse_int_header(headers, HEADER_TOTAL_COUNT),
        "page_count": parse_int_header(headers, HEADER_PAGE_COUNT),
        "page_start": parse_int_header(headers, HEADER_PAGE_START),
        "next_page_url": get(HEADER_NEXT_PAGE_URL) or None,
    }
