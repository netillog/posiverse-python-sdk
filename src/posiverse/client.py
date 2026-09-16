"""Synchronous HTTP client for the Posiverse OpenAPI (v1.1.1).

Authentication uses the ``posiverse-auth-key`` header (OpenAPI security
scheme ``bearerAuth`` is an ``apiKey`` header, not HTTP Bearer). The
client defaults to production. Staff and bots override the host with
``base_url=`` or ``POSIVERSE_BASE_URL``.
"""

from __future__ import annotations

import os
import ssl
from typing import Any, Iterator, Mapping, Optional, Type, TypeVar, Union
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel

from posiverse._utils import drop_none, dump_json_body
from posiverse._version import __version__
from posiverse.config import (
    API_KEY_ENV,
    AUTH_HEADER,
    BASE_URL_ENV,
    DEFAULT_BASE_URL,
    PROD_BASE_URL,
    PosiverseConfig,
)
from posiverse.errors import raise_for_status
from posiverse.pagination import PaginatedResponse, pagination_from_headers
from posiverse.resources.commands import CommandsResource
from posiverse.resources.devices import DevicesResource
from posiverse.resources.firmwares import FirmwaresResource
from posiverse.resources.groups import GroupsResource
from posiverse.resources.logs import LogsResource
from posiverse.resources.products import ProductsResource
from posiverse.resources.settings import SettingsResource
from posiverse.resources.tagmaps import TagMapsResource
from posiverse.resources.tags import TagsResource
from posiverse.resources.tenants import TenantsResource
from posiverse.resources.users import UsersResource
from posiverse.resources.virtual_console import VirtualConsoleResource

T = TypeVar("T", bound=BaseModel)


class HttpBody:
    """Decode HTTP response bodies for the Posiverse client."""

    @staticmethod
    def decode(response: httpx.Response) -> Any:
        """Parse a response body as JSON when possible, else text or None.

        Args:
            response: Completed HTTP response.

        Returns:
            Parsed JSON (dict/list/primitive), a string, or None for empty bodies.
        """
        if not response.content:
            return None
        content_type = response.headers.get("content-type", "")
        # Some error payloads are JSON without a precise content-type; try JSON first.
        try:
            return response.json()
        except ValueError:
            if "json" in content_type.lower():
                return None
            return response.text


class PosiverseClient:
    """Synchronous Posiverse OpenAPI client.

    Resource namespaces match OpenAPI tags: ``commands``, ``devices``,
    ``firmwares``, ``groups``, ``logs``, ``products``, ``settings``,
    ``tagmaps``, ``tags``, ``tenants``, ``users``, ``virtual_console``.

    Args:
        api_key: Posiverse API key sent as the ``posiverse-auth-key`` header.
            When omitted, ``POSIVERSE_API_KEY`` is read from the environment.
        base_url: API server URL. Defaults to production
            (``https://openapi-prod.posiverse.com``), or ``POSIVERSE_BASE_URL``
            when that environment variable is set. Must be https.
        timeout: httpx timeout in seconds, or an ``httpx.Timeout`` instance.
            Defaults to 30 seconds. ``None`` is rejected.
        transport: Optional httpx transport (useful for custom adapters).
        http_client: Existing ``httpx.Client`` to reuse. When provided the
            caller owns its lifecycle unless ``owns_client`` is True. The
            SDK still requires TLS verification on clients it creates.

    Raises:
        ValueError: If no API key is provided and ``POSIVERSE_API_KEY`` is
            unset, if the base URL is not https, or if ``timeout`` is None.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout] = PosiverseConfig.DEFAULT_TIMEOUT_SECONDS,
        transport: Optional[httpx.BaseTransport] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        if api_key is None:
            api_key = os.environ.get(API_KEY_ENV)
        if not api_key:
            raise ValueError(
                "API key required: pass api_key=... or set the POSIVERSE_API_KEY environment variable"
            )

        self._base_url = PosiverseConfig.resolve_base_url(base_url)
        self._api_key = api_key
        self._owns_client = http_client is None
        timeout = PosiverseConfig.coerce_timeout(timeout)

        headers = {
            AUTH_HEADER: api_key,  # apiKey scheme — not "Authorization: Bearer"
            "Accept": "application/json",
            "User-Agent": f"posiverse-python-sdk/{__version__}",
        }

        if http_client is not None:
            PosiverseClient._reject_insecure_http_client(http_client)
            self._http = http_client
            # Ensure the required auth header is present on the shared client.
            self._http.headers[AUTH_HEADER] = api_key
        else:
            self._http = httpx.Client(
                base_url=self._base_url,
                headers=headers,
                timeout=timeout,
                transport=transport,
                verify=True,
            )

        # Resource namespaces — one class per OpenAPI tag.
        self.commands = CommandsResource(self)
        self.devices = DevicesResource(self)
        self.firmwares = FirmwaresResource(self)
        self.groups = GroupsResource(self)
        self.logs = LogsResource(self)
        self.products = ProductsResource(self)
        self.settings = SettingsResource(self)
        self.tagmaps = TagMapsResource(self)
        self.tags = TagsResource(self)
        self.tenants = TenantsResource(self)
        self.users = UsersResource(self)
        self.virtual_console = VirtualConsoleResource(self)

    @staticmethod
    def _ssl_context_of(http_client: httpx.Client) -> Optional[ssl.SSLContext]:
        """Best-effort lookup of the SSL context on an httpx client.

        Args:
            http_client: Existing httpx client.
        """
        transport = getattr(http_client, "_transport", None)
        pool = getattr(transport, "_pool", None)
        context = getattr(pool, "_ssl_context", None)
        return context if isinstance(context, ssl.SSLContext) else None

    @staticmethod
    def _reject_insecure_http_client(http_client: httpx.Client) -> None:
        """Refuse a caller-supplied httpx client that disables TLS verify.

        Args:
            http_client: Existing httpx client.

        Raises:
            ValueError: If TLS verification is explicitly disabled.
        """
        verify = getattr(http_client, "_verify", None)
        if verify is False:
            raise ValueError(
                "http_client must verify TLS; verify=False is not supported"
            )
        ssl_context = PosiverseClient._ssl_context_of(http_client)
        if ssl_context is not None and ssl_context.verify_mode == ssl.CERT_NONE:
            raise ValueError(
                "http_client must verify TLS; verify=False is not supported"
            )

    @property
    def base_url(self) -> str:
        """Return the configured server URL without a trailing slash."""
        return self._base_url

    def close(self) -> None:
        """Close the underlying httpx client when this instance owns it."""
        if self._owns_client:
            self._http.close()

    def __enter__(self) -> "PosiverseClient":
        """Enter a context manager that closes the HTTP client on exit."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Close the HTTP client when leaving the ``with`` block."""
        self.close()

    def __repr__(self) -> str:
        """Return a debug representation that never includes the API key."""
        return (
            f"{self.__class__.__name__}(base_url={self._base_url!r}, "
            f"api_key={PosiverseConfig.redact_secret(self._api_key)})"
        )

    def __str__(self) -> str:
        """Return the same redacted representation as ``repr``."""
        return self.__repr__()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        content: Optional[Union[str, bytes]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> httpx.Response:
        """Send an HTTP request and raise typed errors for non-2xx responses.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, ...).
            path: Path or partial URL relative to ``base_url``. Absolute URLs
                are also accepted (used when following ``x-next-page-url``).
            params: Query string parameters; ``None`` values are dropped.
            json: JSON-serializable body (sent as ``application/json``).
            content: Raw body (used for ``text/plain`` command payloads).
            headers: Extra headers merged into the request.

        Returns:
            The successful ``httpx.Response``.

        Raises:
            BadRequestError: HTTP 400.
            AuthenticationError: HTTP 401.
            ForbiddenError: HTTP 403.
            NotFoundError: HTTP 404.
            RateLimitError: HTTP 429.
            APIError: Other non-2xx responses.
        """
        response = self._http.request(
            method,
            path,
            params=drop_none(params),
            json=json,
            content=content,
            headers=dict(headers) if headers else None,
        )
        body = HttpBody.decode(response)
        # Attach decoded body so request_json/request_paginated can reuse it.
        response.extensions["posiverse_body"] = body
        raise_for_status(response.status_code, body)
        return response

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        content: Optional[Union[str, bytes]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Send a request and return the decoded JSON body.

        Args:
            method: HTTP method.
            path: Path relative to the base URL.
            params: Query string parameters.
            json: JSON request body.
            content: Raw request body.
            headers: Extra headers.

        Returns:
            Parsed JSON, or None when the response has an empty body.

        Raises:
            APIError: On non-2xx responses (see :meth:`request`).
        """
        response = self.request(
            method,
            path,
            params=params,
            json=json,
            content=content,
            headers=headers,
        )
        return response.extensions.get("posiverse_body")

    def request_paginated(
        self,
        method: str,
        path: str,
        *,
        item_model: Type[T],
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
    ) -> PaginatedResponse[T]:
        """Send a list request and wrap items plus pagination headers.

        Args:
            method: HTTP method (typically GET).
            path: Path relative to the base URL.
            item_model: Pydantic model used to validate each array element.
            params: Query string parameters.
            json: Optional JSON body (unused by current list endpoints).

        Returns:
            A :class:`PaginatedResponse` whose ``items`` are ``item_model``
            instances and whose pagination fields come from ``x-*`` headers.

        Raises:
            APIError: On non-2xx responses (see :meth:`request`).
            TypeError: If the JSON body is not a list.
        """
        response = self.request(method, path, params=params, json=json)
        payload = response.extensions.get("posiverse_body")
        if payload is None:
            items: list[T] = []
        elif isinstance(payload, list):
            items = [item_model.model_validate(row) for row in payload]
        else:
            raise TypeError(
                f"Expected a JSON array from {method} {path}, got {type(payload).__name__}"
            )
        meta = pagination_from_headers(response.headers)
        return PaginatedResponse[T](items=items, **meta)

    def follow_next_page(
        self,
        page: PaginatedResponse[T],
        item_model: Type[T],
    ) -> Optional[PaginatedResponse[T]]:
        """Fetch the next page using ``x-next-page-url`` when present.

        The OpenAPI documents ``x-next-page-url`` as a *partial* URL that
        must be prefixed with the original server URL. Absolute URLs are
        passed through unchanged.

        Args:
            page: A previously returned :class:`PaginatedResponse`.
            item_model: Pydantic model for items on the next page.

        Returns:
            The next :class:`PaginatedResponse`, or None when there is no
            next page.

        Raises:
            APIError: On non-2xx responses (see :meth:`request`).
        """
        if not page.next_page_url:
            return None
        # Prefer a path (plus query) relative to this client so httpx keeps
        # using the configured base URL. Absolute URLs on a different host
        # are passed through unchanged.
        next_url = page.next_page_url
        parsed = urlparse(next_url)
        if parsed.scheme and parsed.netloc:
            # Same host as this client: drop the scheme/host so base_url applies.
            if parsed.netloc == urlparse(self.base_url).netloc:
                next_url = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        return self.request_paginated("GET", next_url, item_model=item_model)

    def iter_pages(
        self,
        method: str,
        path: str,
        *,
        item_model: Type[T],
        params: Optional[Mapping[str, Any]] = None,
    ) -> Iterator[PaginatedResponse[T]]:
        """Yield successive pages until ``x-next-page-url`` is absent.

        Args:
            method: HTTP method for the first request.
            path: Path relative to the base URL.
            item_model: Pydantic model for each item.
            params: Query string parameters for the first request. Subsequent
                pages use the server-provided next URL as-is.

        Yields:
            Each :class:`PaginatedResponse` in order.

        Raises:
            APIError: On non-2xx responses (see :meth:`request`).
        """
        page = self.request_paginated(method, path, item_model=item_model, params=params)
        while True:
            yield page
            nxt = self.follow_next_page(page, item_model)
            if nxt is None:
                return
            page = nxt

    def dump_body(self, body: Any) -> Any:
        """Serialize a pydantic model for a JSON request body.

        Args:
            body: A pydantic model, mapping, or None.

        Returns:
            JSON-serializable data suitable for httpx ``json=``.
        """
        return dump_json_body(body)


__all__ = [
    "API_KEY_ENV",
    "AUTH_HEADER",
    "BASE_URL_ENV",
    "DEFAULT_BASE_URL",
    "HttpBody",
    "PROD_BASE_URL",
    "PosiverseClient",
    "PosiverseConfig",
]
