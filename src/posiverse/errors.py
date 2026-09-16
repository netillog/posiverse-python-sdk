"""Exception hierarchy for Posiverse API errors.

Maps HTTP status codes used by the OpenAPI to typed exceptions so callers
can handle auth, validation, and rate-limit failures distinctly.
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

    Args:
        status_code: HTTP response status code.
        body: Parsed response body used to enrich the error message.

    Raises:
        APIError: Subclass matching the status code, or a generic APIError
            for other non-2xx codes.
    """
    if 200 <= status_code < 300:
        return

    # Prefer structured Error schema fields when present.
    message = f"HTTP {status_code}"
    if isinstance(body, dict):
        message = str(body.get("message") or body.get("error") or message)
        if "code" in body and body.get("message"):
            message = f"{body['code']}: {body['message']}"
    elif isinstance(body, str) and body:
        message = body

    exc_cls = STATUS_ERROR_MAP.get(status_code, APIError)
    raise exc_cls(message, status_code=status_code, body=body)
