"""Exception hierarchy for Posiverse API errors.

Maps HTTP status codes declared in the OpenAPI (400, 401, 403, 404, 429)
to typed exceptions so callers can handle auth, validation, and
rate-limit failures distinctly. Other non-2xx codes raise :class:`APIError`.
"""

from __future__ import annotations

from typing import Any, Optional


class APIError(Exception):
    """Base exception for all Posiverse API failures.

    Args:
        message: Human-readable error description.
        status_code: HTTP status code when available.
        body: Raw response body (JSON dict, string, or None).
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.body = body

    def __str__(self) -> str:
        """Return ``[status] message`` when a status code is known."""
        if self.status_code is not None:
            return f"[{self.status_code}] {self.message}"
        return self.message


class BadRequestError(APIError):
    """Raised for HTTP 400 Bad Request responses."""


class AuthenticationError(APIError):
    """Raised for HTTP 401 Unauthorized responses (missing/invalid API key)."""


class ForbiddenError(APIError):
    """Raised for HTTP 403 Forbidden responses (insufficient permissions)."""


class NotFoundError(APIError):
    """Raised for HTTP 404 Not Found responses."""


class RateLimitError(APIError):
    """Raised for HTTP 429 Too Many Requests responses."""


# Status-code → exception class mapping used by the HTTP client.
STATUS_ERROR_MAP: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    429: RateLimitError,
}


def raise_for_status(status_code: int, body: Any = None) -> None:
    """Raise a typed APIError when ``status_code`` indicates failure.

    Prefers the OpenAPI ``Error`` schema fields ``code`` and ``message``
    when the body is a JSON object.

    Args:
        status_code: HTTP response status code.
        body: Parsed response body used to enrich the error message.

    Raises:
        APIError: Subclass matching 400/401/403/404/429, or a generic
            APIError for other non-2xx codes.
    """
    if 200 <= status_code < 300:
        return

    # Prefer structured Error schema fields when present.
    message = f"HTTP {status_code}"
    if isinstance(body, dict):
        code = body.get("code")
        text = body.get("message") or body.get("error")
        if code is not None and text:
            message = f"{code}: {text}"
        elif text:
            message = str(text)
    elif isinstance(body, str) and body:
        message = body

    exc_cls = STATUS_ERROR_MAP.get(status_code, APIError)
    raise exc_cls(message, status_code=status_code, body=body)
