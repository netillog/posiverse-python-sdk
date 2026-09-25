"""Posiverse Python SDK — typed client for the Posiverse OpenAPI (v1.1.1).

Quickstart::

    from posiverse import PosiverseClient

    # API key via POSIVERSE_API_KEY, a project-root .env, or pass api_key=...
    # Default base URL is production. Staff/bots may set POSIVERSE_BASE_URL.
    with PosiverseClient() as client:
        page = client.devices.list()
        for device in page.items:
            print(device.id, device.name)
"""

from posiverse._version import __version__
from posiverse.client import HttpBody, PosiverseClient
from posiverse.config import (
    API_KEY_ENV,
    AUTH_HEADER,
    BASE_URL_ENV,
    DEFAULT_BASE_URL,
    PROD_BASE_URL,
    PosiverseConfig,
)
from posiverse.device_logs import DeviceLogQueries, ReportIdentity
from posiverse.errors import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
)
from posiverse.pagination import PaginatedResponse

__all__ = [
    "API_KEY_ENV",
    "AUTH_HEADER",
    "BASE_URL_ENV",
    "DEFAULT_BASE_URL",
    "DeviceLogQueries",
    "HttpBody",
    "PROD_BASE_URL",
    "ReportIdentity",
    "APIError",
    "AuthenticationError",
    "BadRequestError",
    "ForbiddenError",
    "NotFoundError",
    "PaginatedResponse",
    "PosiverseClient",
    "PosiverseConfig",
    "RateLimitError",
    "__version__",
]
