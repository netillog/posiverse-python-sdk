"""Posiverse Python SDK — typed client for the Posiverse OpenAPI (v1.1.1).

Quickstart::

    import os
    from posiverse import PosiverseClient

    # API key via env POSIVERSE_API_KEY (or pass api_key=...)
    with PosiverseClient() as client:
        page = client.devices.list()
        for device in page.items:
            print(device.id, device.name)

Default base URL is the test server
(``https://openapi-test.posiverse.com``). Production is available as
``PROD_BASE_URL`` but live tests must never target production.
"""

from posiverse.client import (
    API_KEY_ENV,
    AUTH_HEADER,
    DEFAULT_BASE_URL,
    PROD_BASE_URL,
    TEST_BASE_URL,
    PosiverseClient,
)
from posiverse.errors import (
    APIError,
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
)
from posiverse.pagination import PaginatedResponse

__version__ = "0.1.0"

__all__ = [
    "API_KEY_ENV",
    "AUTH_HEADER",
    "DEFAULT_BASE_URL",
    "PROD_BASE_URL",
    "TEST_BASE_URL",
    "APIError",
    "AuthenticationError",
    "BadRequestError",
    "ForbiddenError",
    "NotFoundError",
    "PaginatedResponse",
    "PosiverseClient",
    "RateLimitError",
    "__version__",
]
